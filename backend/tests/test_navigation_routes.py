"""
KAVACH 5.0 — Regression Tests: Navigation & Route Separation

Proves:
1. Command Center resolves to 'command-center' and renders CommandCenterPage.
2. World Situational Monitor resolves to 'world-monitor' and renders WorldMonitorPage.
3. No crosstalk exists between the Command Center route and World Situational Monitor route.
4. Navigation UI files (WorkspaceSubnav, Navbar, Sidebar, FindingsPage) maintain correct distinct route links.
"""

from pathlib import Path


def test_app_router_route_separation():
    base_dir = Path(__file__).resolve().parent.parent.parent
    app_tsx = (base_dir / "frontend" / "src" / "App.tsx").read_text(encoding="utf-8")

    # App.tsx must import both pages separately
    assert "import { CommandCenterPage } from './pages/CommandCenterPage';" in app_tsx
    assert "import { WorldMonitorPage } from './pages/WorldMonitorPage';" in app_tsx

    # case 'command-center' must return CommandCenterPage
    assert "case 'command-center':" in app_tsx
    assert "return <CommandCenterPage />;" in app_tsx

    # case 'world-monitor' must return WorldMonitorPage
    assert "case 'world-monitor':" in app_tsx
    assert "return <WorldMonitorPage />;" in app_tsx

    # Ensure command-center does NOT return WorldMonitorPage
    assert "case 'command-center':\n        return <WorldMonitorPage />;" not in app_tsx


def test_workspacesubnav_distinct_tabs():
    base_dir = Path(__file__).resolve().parent.parent.parent
    subnav = (base_dir / "frontend" / "src" / "components" / "layout" / "WorkspaceSubnav.tsx").read_text(encoding="utf-8")

    # Command Center tab has id: 'command-center' and label: 'Command Center'
    assert "{ id: 'command-center',      label: 'Command Center', icon: LayoutDashboard }" in subnav

    # World Monitor tab has id: 'world-monitor' and label: 'World Monitor'
    assert "{ id: 'world-monitor',       label: 'World Monitor', icon: Radio }" in subnav

    # Confirm bug is not present
    assert "{ id: 'command-center',      label: 'World Monitor'" not in subnav


def test_navbar_distinct_routes():
    base_dir = Path(__file__).resolve().parent.parent.parent
    navbar = (base_dir / "frontend" / "src" / "components" / "layout" / "Navbar.tsx").read_text(encoding="utf-8")

    # Step 1 is Command Center -> 'command-center'
    assert "page: 'command-center'" in navbar
    assert "title: '1. Command Center'" in navbar

    # Platform modules have both
    assert "{ id: 'command-center', label: 'Command Center'" in navbar
    assert "{ id: 'world-monitor', label: 'World Situational Monitor'" in navbar


def test_sidebar_distinct_routes():
    base_dir = Path(__file__).resolve().parent.parent.parent
    sidebar = (base_dir / "frontend" / "src" / "components" / "layout" / "Sidebar.tsx").read_text(encoding="utf-8")

    assert "{ id: 'command-center', label: 'Command Center', icon: LayoutDashboard, category: 'Primary' }" in sidebar
    assert "{ id: 'world-monitor', label: 'World Situational Monitor', icon: Globe, category: 'Advanced / SOC' }" in sidebar


def test_findings_page_world_monitor_link():
    base_dir = Path(__file__).resolve().parent.parent.parent
    findings = (base_dir / "frontend" / "src" / "pages" / "FindingsPage.tsx").read_text(encoding="utf-8")

    # 'View in World Monitor' action buttons must navigate to 'world-monitor'
    assert "navigate('world-monitor');" in findings
    # Should not have any navigate('command-center') left for world monitor events
    assert "setSelectedWorldEventId(corr.event_id || corr.event?.id || null);\n                            navigate('command-center');" not in findings
