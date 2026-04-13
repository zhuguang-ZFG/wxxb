"""代理节点管理器 - 自动验证和更新节点"""

from __future__ import annotations

import json
import logging
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import requests

logger = logging.getLogger(__name__)


class ProxyNodeManager:
    """代理节点管理器
    
    功能：
    - 验证代理节点可用性
    - 从 GitHub 自动拉取节点
    - 管理节点缓存
    - 自动清除失效节点
    """
    
    def __init__(self, cache_dir: Path | None = None):
        """初始化节点管理器
        
        Args:
            cache_dir: 缓存目录，默认为 ~/.linktunnel/proxy_nodes
        """
        if cache_dir is None:
            cache_dir = Path.home() / ".linktunnel" / "proxy_nodes"
        
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.nodes_file = self.cache_dir / "nodes.json"
        self.status_file = self.cache_dir / "status.json"
        
        self._nodes: dict[str, dict[str, Any]] = {}
        self._status: dict[str, dict[str, Any]] = {}
        self._lock = threading.Lock()
        
        self._load_cache()
    
    def _load_cache(self) -> None:
        """加载缓存的节点数据"""
        try:
            if self.nodes_file.exists():
                with open(self.nodes_file, "r", encoding="utf-8") as f:
                    self._nodes = json.load(f)
            
            if self.status_file.exists():
                with open(self.status_file, "r", encoding="utf-8") as f:
                    self._status = json.load(f)
        except Exception as e:
            logger.error(f"加载缓存失败: {e}")
            self._nodes = {}
            self._status = {}
    
    def _save_cache(self) -> None:
        """保存缓存的节点数据"""
        try:
            with open(self.nodes_file, "w", encoding="utf-8") as f:
                json.dump(self._nodes, f, ensure_ascii=False, indent=2)
            
            with open(self.status_file, "w", encoding="utf-8") as f:
                json.dump(self._status, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存缓存失败: {e}")
    
    def add_node(self, name: str, url: str, source: str = "manual") -> bool:
        """添加节点
        
        Args:
            name: 节点名称
            url: 订阅 URL
            source: 节点来源 (manual/github/subscription)
        
        Returns:
            是否添加成功
        """
        with self._lock:
            if name in self._nodes:
                logger.warning(f"节点 {name} 已存在")
                return False
            
            self._nodes[name] = {
                "url": url,
                "source": source,
                "added_at": datetime.now().isoformat(),
            }
            
            self._status[name] = {
                "valid": None,
                "last_check": None,
                "error": None,
            }
            
            self._save_cache()
            logger.info(f"已添加节点: {name}")
            return True
    
    def remove_node(self, name: str) -> bool:
        """移除节点
        
        Args:
            name: 节点名称
        
        Returns:
            是否移除成功
        """
        with self._lock:
            if name not in self._nodes:
                logger.warning(f"节点 {name} 不存在")
                return False
            
            del self._nodes[name]
            if name in self._status:
                del self._status[name]
            
            self._save_cache()
            logger.info(f"已移除节点: {name}")
            return True
    
    def verify_node(self, name: str, timeout: float = 10.0) -> bool:
        """验证单个节点
        
        Args:
            name: 节点名称
            timeout: 超时时间（秒）
        
        Returns:
            节点是否有效
        """
        if name not in self._nodes:
            logger.warning(f"节点 {name} 不存在")
            return False
        
        node_info = self._nodes[name]
        url = node_info.get("url", "")
        
        try:
            # 验证 URL 格式
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                raise ValueError(f"无效的 URL: {url}")
            
            # 尝试连接
            response = requests.get(
                url,
                timeout=timeout,
                allow_redirects=True,
                headers={"User-Agent": "linktunnel/1.0"}
            )
            
            valid = response.status_code == 200
            
            with self._lock:
                self._status[name] = {
                    "valid": valid,
                    "last_check": datetime.now().isoformat(),
                    "error": None if valid else f"HTTP {response.status_code}",
                }
                self._save_cache()
            
            logger.info(f"节点 {name} 验证: {'✓' if valid else '✗'}")
            return valid
        
        except Exception as e:
            error_msg = str(e)
            with self._lock:
                self._status[name] = {
                    "valid": False,
                    "last_check": datetime.now().isoformat(),
                    "error": error_msg,
                }
                self._save_cache()
            
            logger.error(f"节点 {name} 验证失败: {error_msg}")
            return False
    
    def verify_all_nodes(self, timeout: float = 10.0) -> dict[str, bool]:
        """验证所有节点
        
        Args:
            timeout: 超时时间（秒）
        
        Returns:
            节点名称 -> 是否有效的映射
        """
        results = {}
        threads = []
        
        def verify_worker(name: str) -> None:
            results[name] = self.verify_node(name, timeout)
        
        # 并行验证
        for name in list(self._nodes.keys()):
            thread = threading.Thread(target=verify_worker, args=(name,), daemon=True)
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join(timeout=timeout + 5)
        
        return results
    
    def cleanup_invalid_nodes(self) -> list[str]:
        """清除失效的节点
        
        Returns:
            被清除的节点名称列表
        """
        removed = []
        
        with self._lock:
            for name in list(self._nodes.keys()):
                status = self._status.get(name, {})
                if status.get("valid") is False:
                    # 检查是否已经失效超过 7 天
                    last_check = status.get("last_check")
                    if last_check:
                        try:
                            check_time = datetime.fromisoformat(last_check)
                            if datetime.now() - check_time > timedelta(days=7):
                                del self._nodes[name]
                                del self._status[name]
                                removed.append(name)
                                logger.info(f"已清除失效节点: {name}")
                        except Exception as e:
                            logger.error(f"处理节点 {name} 时出错: {e}")
            
            if removed:
                self._save_cache()
        
        return removed
    
    def fetch_from_github(self, repo: str, file_path: str = "nodes.txt") -> list[str]:
        """从 GitHub 拉取节点列表
        
        Args:
            repo: GitHub 仓库 (格式: owner/repo)
            file_path: 文件路径 (默认: nodes.txt)
        
        Returns:
            新增的节点名称列表
        """
        try:
            # 构建 GitHub 原始文件 URL
            url = f"https://raw.githubusercontent.com/{repo}/main/{file_path}"
            
            response = requests.get(
                url,
                timeout=10,
                headers={"User-Agent": "linktunnel/1.0"}
            )
            response.raise_for_status()
            
            # 解析节点列表
            lines = response.text.strip().split("\n")
            new_nodes = []
            
            for i, line in enumerate(lines):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                
                # 假设格式为: name|url 或 url
                if "|" in line:
                    name, node_url = line.split("|", 1)
                    name = name.strip()
                    node_url = node_url.strip()
                else:
                    name = f"github_{i}"
                    node_url = line
                
                if self.add_node(name, node_url, source="github"):
                    new_nodes.append(name)
            
            logger.info(f"从 GitHub 拉取了 {len(new_nodes)} 个新节点")
            return new_nodes
        
        except Exception as e:
            logger.error(f"从 GitHub 拉取节点失败: {e}")
            return []
    
    def fetch_from_subscription(self, url: str) -> list[str]:
        """从订阅 URL 拉取节点
        
        Args:
            url: 订阅 URL
        
        Returns:
            新增的节点名称列表
        """
        try:
            response = requests.get(
                url,
                timeout=10,
                headers={"User-Agent": "linktunnel/1.0"}
            )
            response.raise_for_status()
            
            # 解析订阅内容
            lines = response.text.strip().split("\n")
            new_nodes = []
            
            for i, line in enumerate(lines):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                
                # 假设格式为: name|url 或 url
                if "|" in line:
                    name, node_url = line.split("|", 1)
                    name = name.strip()
                    node_url = node_url.strip()
                else:
                    name = f"sub_{i}"
                    node_url = line
                
                if self.add_node(name, node_url, source="subscription"):
                    new_nodes.append(name)
            
            logger.info(f"从订阅拉取了 {len(new_nodes)} 个新节点")
            return new_nodes
        
        except Exception as e:
            logger.error(f"从订阅拉取节点失败: {e}")
            return []
    
    def search_github_hotspot_repos(self, keyword: str = "proxy", language: str = "python") -> list[dict[str, str]]:
        """从 GitHub 搜索开放的热点节点仓库
        
        Args:
            keyword: 搜索关键词 (默认: proxy)
            language: 编程语言 (默认: python)
        
        Returns:
            仓库信息列表 [{"name": "...", "url": "...", "description": "..."}]
        """
        try:
            # 搜索 GitHub 仓库
            search_url = "https://api.github.com/search/repositories"
            params = {
                "q": f"{keyword} language:{language} stars:>100",
                "sort": "stars",
                "order": "desc",
                "per_page": 10,
            }
            
            response = requests.get(
                search_url,
                params=params,
                timeout=10,
                headers={"User-Agent": "linktunnel/1.0"}
            )
            response.raise_for_status()
            
            data = response.json()
            repos = []
            
            for item in data.get("items", []):
                repo_info = {
                    "name": item.get("name", ""),
                    "full_name": item.get("full_name", ""),
                    "url": item.get("html_url", ""),
                    "description": item.get("description", ""),
                    "stars": item.get("stargazers_count", 0),
                    "language": item.get("language", ""),
                }
                repos.append(repo_info)
            
            logger.info(f"从 GitHub 搜索到 {len(repos)} 个热点仓库")
            return repos
        
        except Exception as e:
            logger.error(f"搜索 GitHub 仓库失败: {e}")
            return []
    
    def fetch_from_github_hotspot(self, keyword: str = "proxy", language: str = "python") -> list[str]:
        """从 GitHub 热点仓库自动拉取节点
        
        Args:
            keyword: 搜索关键词
            language: 编程语言
        
        Returns:
            新增的节点名称列表
        """
        new_nodes = []
        
        try:
            # 搜索热点仓库
            repos = self.search_github_hotspot_repos(keyword, language)
            
            for repo in repos:
                try:
                    full_name = repo.get("full_name", "")
                    if not full_name:
                        continue
                    
                    # 尝试从常见文件拉取节点
                    file_paths = [
                        "nodes.txt",
                        "nodes.json",
                        "README.md",
                        "subscribe.txt",
                        "proxy.txt",
                        "list.txt",
                    ]
                    
                    for file_path in file_paths:
                        try:
                            url = f"https://raw.githubusercontent.com/{full_name}/main/{file_path}"
                            response = requests.get(
                                url,
                                timeout=5,
                                headers={"User-Agent": "linktunnel/1.0"}
                            )
                            
                            if response.status_code == 200:
                                # 解析节点
                                lines = response.text.strip().split("\n")
                                for i, line in enumerate(lines):
                                    line = line.strip()
                                    if not line or line.startswith("#"):
                                        continue
                                    
                                    # 假设格式为: name|url 或 url
                                    if "|" in line:
                                        name, node_url = line.split("|", 1)
                                        name = name.strip()
                                        node_url = node_url.strip()
                                    else:
                                        name = f"github_{repo['name']}_{i}"
                                        node_url = line
                                    
                                    if self.add_node(name, node_url, source="github_hotspot"):
                                        new_nodes.append(name)
                                
                                logger.info(f"从 {full_name}/{file_path} 拉取了 {len(lines)} 个节点")
                                break
                        
                        except Exception as e:
                            logger.debug(f"尝试 {full_name}/{file_path} 失败: {e}")
                            continue
                
                except Exception as e:
                    logger.error(f"处理仓库 {repo.get('full_name')} 失败: {e}")
                    continue
            
            logger.info(f"从 GitHub 热点仓库拉取了 {len(new_nodes)} 个新节点")
            return new_nodes
        
        except Exception as e:
            logger.error(f"从 GitHub 热点仓库拉取节点失败: {e}")
            return []
    
    def auto_fetch_hotspot_nodes(self) -> dict[str, Any]:
        """自动从 GitHub 热点仓库拉取节点
        
        Returns:
            拉取结果 {"repos": 仓库数, "nodes": 节点数, "timestamp": 时间}
        """
        try:
            logger.info("开始自动拉取 GitHub 热点节点...")
            
            # 搜索热点仓库
            repos = self.search_github_hotspot_repos()
            
            # 拉取节点
            new_nodes = self.fetch_from_github_hotspot()
            
            result = {
                "repos": len(repos),
                "nodes": len(new_nodes),
                "timestamp": datetime.now().isoformat(),
            }
            
            logger.info(f"自动拉取完成: {len(repos)} 个仓库, {len(new_nodes)} 个新节点")
            return result
        
        except Exception as e:
            logger.error(f"自动拉取失败: {e}")
            return {"repos": 0, "nodes": 0, "error": str(e)}
    
    def get_nodes(self) -> dict[str, dict[str, Any]]:
        """获取所有节点
        
        Returns:
            节点信息字典
        """
        with self._lock:
            return dict(self._nodes)
    
    def get_status(self) -> dict[str, dict[str, Any]]:
        """获取所有节点的状态
        
        Returns:
            节点状态字典
        """
        with self._lock:
            return dict(self._status)
    
    def get_valid_nodes(self) -> list[str]:
        """获取所有有效的节点
        
        Returns:
            有效节点名称列表
        """
        with self._lock:
            return [
                name for name, status in self._status.items()
                if status.get("valid") is True
            ]
    
    def get_invalid_nodes(self) -> list[str]:
        """获取所有失效的节点
        
        Returns:
            失效节点名称列表
        """
        with self._lock:
            return [
                name for name, status in self._status.items()
                if status.get("valid") is False
            ]
    
    def schedule_daily_update(self, callback=None) -> None:
        """调度每日更新任务
        
        Args:
            callback: 更新完成后的回调函数
        """
        def update_worker() -> None:
            while True:
                try:
                    # 计算下次更新时间（每天凌晨 2 点）
                    now = datetime.now()
                    next_update = now.replace(hour=2, minute=0, second=0, microsecond=0)
                    if next_update <= now:
                        next_update += timedelta(days=1)
                    
                    wait_seconds = (next_update - now).total_seconds()
                    logger.info(f"下次节点更新时间: {next_update}")
                    
                    time.sleep(wait_seconds)
                    
                    # 执行更新
                    logger.info("开始每日节点更新...")
                    self.verify_all_nodes()
                    removed = self.cleanup_invalid_nodes()
                    
                    if callback:
                        callback({
                            "verified": len(self._nodes),
                            "removed": len(removed),
                            "timestamp": datetime.now().isoformat(),
                        })
                    
                    logger.info(f"每日更新完成: 验证 {len(self._nodes)} 个节点, 清除 {len(removed)} 个失效节点")
                
                except Exception as e:
                    logger.error(f"每日更新失败: {e}")
                    time.sleep(3600)  # 出错后等待 1 小时重试
        
        thread = threading.Thread(target=update_worker, daemon=True)
        thread.start()
        logger.info("已启动每日节点更新任务")
