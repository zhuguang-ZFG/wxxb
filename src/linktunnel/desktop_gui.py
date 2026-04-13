from __future__ import annotations

import click

from linktunnel.dashboard_open import local_embedded_ui_url, yacd_meta_browser_url
from linktunnel.proxy.mihomo_config import (
    default_profile_dir,
    external_controller_hints_from_config,
)


def run_desktop_app(
    *,
    from_profile: bool,
    panel: str,
    api: str,
    secret: str,
    width: int,
    height: int,
    title: str,
) -> None:
    """
    Open a standalone OS window with an embedded WebView (pywebview).

    Cross-platform (Windows / macOS / Linux); system WebView2 / WebKit / GTK WebKit required.
    """
    try:
        import webview  # type: ignore[import-untyped]
    except ImportError as e:
        raise click.ClickException(
            "独立桌面窗口需要安装可选依赖：\n"
            "  pip install 'linktunnel[desktop]'\n"
            "Linux 若缺 WebKit，请安装发行版说明中的 webview 依赖。"
        ) from e

    api_u = api.strip()
    secret_u = secret
    if from_profile:
        cfg = default_profile_dir() / "config.yaml"
        if not cfg.is_file():
            raise click.ClickException(
                f"未找到 {cfg}，请先执行：linktunnel proxy init …\n"
                "或去掉 --from-profile，改用 --api / --secret。"
            )
        api_u, secret_u = external_controller_hints_from_config(cfg)

    if panel == "local":
        url = local_embedded_ui_url(api_u)
    else:
        url = yacd_meta_browser_url(api_u, secret_u)

    webview.create_window(
        title,
        url,
        width=width,
        height=height,
        min_size=(640, 480),
    )
    webview.start()


def gui_main() -> None:
    """Console entry ``linktunnel-gui`` → 等价于 ``linktunnel gui``。"""
    import sys

    sys.argv = [sys.argv[0], "gui", *sys.argv[1:]]
    from linktunnel.cli import main

    main()
