#!/usr/bin/env bash
# Instala lo necesario (Docker, Node.js) y levanta el proyecto Granero.
# Uso: ./scripts/setup.sh   (desde la raiz del repo, o desde donde sea)

set -e

cd "$(dirname "$0")/.."

step() { echo -e "\n==> $1"; }
ok()   { echo "    OK: $1"; }
warn() { echo "    AVISO: $1"; }
check_cmd() { command -v "$1" >/dev/null 2>&1; }

OS="$(uname -s)"

echo "==================================================="
echo "  Granero - instalador y arranque del proyecto"
echo "==================================================="

step "Verificando Docker"
if check_cmd docker; then
  ok "Docker ya esta instalado"
else
  step "Docker no encontrado. Instalando..."
  if [ "$OS" = "Darwin" ]; then
    if ! check_cmd brew; then
      warn "Se requiere Homebrew para instalar Docker automaticamente en macOS."
      echo "    Instalalo desde https://brew.sh y vuelve a ejecutar este script."
      exit 1
    fi
    brew install --cask docker
    warn "Abre la app Docker Desktop una vez manualmente para completar la instalacion,"
    warn "acepta sus terminos de uso, y luego vuelve a ejecutar este script."
    open -a Docker || true
  elif [ "$OS" = "Linux" ]; then
    curl -fsSL https://get.docker.com | sh
    warn "Es posible que necesites cerrar sesion y volver a entrar para usar Docker sin sudo."
  else
    warn "Sistema operativo no reconocido. Instala Docker manualmente: https://docs.docker.com/get-docker/"
    exit 1
  fi
fi

step "Verificando Node.js (opcional, mejora el autocompletado del editor)"
if check_cmd node; then
  ok "Node.js ya esta instalado ($(node --version))"
else
  step "Node.js no encontrado. Instalando..."
  if [ "$OS" = "Darwin" ] && check_cmd brew; then
    brew install node
  elif [ "$OS" = "Linux" ]; then
    curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
    sudo apt-get install -y nodejs
  else
    warn "Instala Node.js manualmente: https://nodejs.org"
  fi
fi

step "Esperando a que Docker este corriendo"
elapsed=0
until docker info >/dev/null 2>&1; do
  if [ "$elapsed" -ge 120 ]; then
    warn "Docker no respondio a tiempo. Abrelo manualmente y vuelve a ejecutar este script."
    exit 1
  fi
  echo "    Docker aun no responde, esperando..."
  sleep 3
  elapsed=$((elapsed + 3))
done
ok "Docker esta corriendo"

step "Preparando archivo .env"
if [ ! -f .env ]; then
  cp .env.example .env
  ok ".env creado a partir de .env.example"
else
  ok ".env ya existe, no se sobreescribe"
fi

if check_cmd npm; then
  step "Instalando dependencias del frontend localmente (para el editor)"
  (cd frontend && npm install --no-audit --no-fund) || warn "No se pudieron instalar (no es critico, Docker las instala igual)"
fi

step "Construyendo y levantando los contenedores (la primera vez puede tardar varios minutos)"
docker compose up -d --build

step "Esperando a que el backend responda"
elapsed=0
backend_ready=false
until [ "$backend_ready" = true ]; do
  if curl -sf http://localhost:8000/health >/dev/null 2>&1; then
    backend_ready=true
    break
  fi
  if [ "$elapsed" -ge 120 ]; then
    warn "El backend tardo en responder. Revisa los logs con: docker compose logs backend"
    break
  fi
  sleep 3
  elapsed=$((elapsed + 3))
done
[ "$backend_ready" = true ] && ok "Backend listo"

echo ""
echo "==================================================="
echo "  Listo!"
echo "==================================================="
echo ""
echo "  Frontend:  http://localhost:5173"
echo "  API/Docs:  http://localhost:8000/docs"
echo "  Adminer:   http://localhost:8080"
echo ""
echo "  Usuario demo:     admin@granero.com"
echo "  Contrasena demo:  admin123"
echo ""

if [ "$OS" = "Darwin" ]; then
  open http://localhost:5173 || true
elif check_cmd xdg-open; then
  xdg-open http://localhost:5173 || true
fi
