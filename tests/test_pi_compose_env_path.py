from pathlib import Path


def test_pi_compose_reads_installer_root_env_file():
    root = Path(__file__).resolve().parents[1]
    compose = (root / "pi" / "docker-compose.pi.yml").read_text()
    installer = (root / "pi" / "install.sh").read_text()

    assert 'COMPOSE_FILE="pi/docker-compose.pi.yml"' in installer
    assert "cp -f .env.example .env" in installer
    assert compose.count("env_file: ../.env") == 2
    assert "env_file: .env" not in compose
