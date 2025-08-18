REACT_WITH_VITE_TEMPLATE="""
# --- Prerequisites check ---
bun --version || echo "Bun not found"
node --version || echo "Node.js not found"
git --version || echo "Git not found"

# --- Installation ---
# Linux (Debian/Ubuntu)
sudo apt update
sudo apt install -y curl git nodejs npm
curl -fsSL https://bun.sh/install | bash

# Linux (Arch)
sudo pacman -S --needed nodejs npm git curl
curl -fsSL https://bun.sh/install | bash

# macOS
brew install node git
curl -fsSL https://bun.sh/install | bash

# Windows (PowerShell)
winget install OpenJS.NodeJS Git.Git
irm bun.sh/install.ps1 | iex

# --- Project Setup ---
bun create vite@latest my-vite-react-app --template react-ts
cd my-vite-react-app
bun install

# --- Run Dev Server ---
bun dev
"""


REACT_TEMPLATE="""
# --- Prerequisites check ---
bun --version || echo "Bun not found"
node --version || echo "Node.js not found"
git --version || echo "Git not found"

# --- Installation ---
# Debian/Ubuntu
sudo apt update
sudo apt install -y nodejs npm git curl
curl -fsSL https://bun.sh/install | bash

# Arch
sudo pacman -S --needed nodejs npm git curl
curl -fsSL https://bun.sh/install | bash

# macOS
brew install node git
curl -fsSL https://bun.sh/install | bash

# Windows
winget install OpenJS.NodeJS Git.Git
irm bun.sh/install.ps1 | iex

# --- Project Setup ---
bun create react my-react-app --ts
cd my-react-app
bun install

# --- Run Dev Server ---
bun run start
"""

REACT_WITH_NODE_JS_TEMPLATE="""
# --- Prerequisites check ---
bun --version || echo "Bun not found"
node --version || echo "Node.js not found"
git --version || echo "Git not found"

# --- Installation ---
# Debian/Ubuntu
sudo apt update
sudo apt install -y nodejs npm git curl
curl -fsSL https://bun.sh/install | bash

# Arch
sudo pacman -S --needed nodejs npm git curl
curl -fsSL https://bun.sh/install | bash

# macOS
brew install node git
curl -fsSL https://bun.sh/install | bash

# Windows (PowerShell)
winget install OpenJS.NodeJS Git.Git
irm bun.sh/install.ps1 | iex

# --- Project Setup ---
mkdir react-node-app && cd react-node-app

# --- Backend Setup ---
mkdir backend && cd backend
bun init -y

# Install backend deps
bun add express @types/express tsx typescript

# Create basic server entry point
cat > index.ts << 'EOF'
import express from "express";

const app = express();
const port = 3000;

app.get("/", (_req, res) => {
  res.send("Hello from Express + Bun + TypeScript backend!");
});

app.listen(port, () => {
  console.log(`Server running on http://localhost:${port}`);
});
EOF

cd ..

# --- Frontend Setup ---
mkdir frontend && cd frontend
bun create vite@latest . --template react-ts
bun install
cd ..

# --- Project Structure ---
# /
# ├── backend
# │   ├── index.ts
# │   └── package.json (bun-managed)
# └── frontend
#     ├── vite.config.ts
#     ├── src/
#     └── package.json (bun-managed)

# --- Run Backend ---
cd backend
bun run tsx index.ts

# --- Run Frontend ---
cd ../frontend
bun dev

"""

NEXT_JS_TEMPLATE="""
# --- Prerequisites check ---
bun --version || echo "Bun not found"
node --version || echo "Node.js not found"
git --version || echo "Git not found"

# --- Installation ---
# Debian/Ubuntu
sudo apt update
sudo apt install -y nodejs npm git curl
curl -fsSL https://bun.sh/install | bash

# Arch
sudo pacman -S --needed nodejs npm git curl
curl -fsSL https://bun.sh/install | bash

# macOS
brew install node git
curl -fsSL https://bun.sh/install | bash

# Windows
winget install OpenJS.NodeJS Git.Git
irm bun.sh/install.ps1 | iex

# --- Project Setup ---
bun create next-app my-next-app --ts
cd my-next-app

# --- Run Dev Server ---
bun dev
"""

ANGULAR_JS_TEMPLATE="""
# --- Prerequisites check ---
bun --version || echo "Bun not found"
node --version || echo "Node.js not found"
git --version || echo "Git not found"

# --- Installation ---
# Debian/Ubuntu
sudo apt update
sudo apt install -y nodejs npm git curl
curl -fsSL https://bun.sh/install | bash

# Arch
sudo pacman -S --needed nodejs npm git curl
curl -fsSL https://bun.sh/install | bash

# macOS
brew install node git
curl -fsSL https://bun.sh/install | bash

# Windows
winget install OpenJS.NodeJS Git.Git
irm bun.sh/install.ps1 | iex

# --- Project Setup ---
bun add -g @angular/cli
ng new my-angular-app --defaults --strict --style=scss --skip-git --package-manager=bun
cd my-angular-app

# --- Run Dev Server ---
bun ng serve
"""

VUE_JS_TEMPLATE="""
# --- Prerequisites check ---
bun --version || echo "Bun not found"
node --version || echo "Node.js not found"
git --version || echo "Git not found"

# --- Installation ---
# Debian/Ubuntu
sudo apt update
sudo apt install -y nodejs npm git curl
curl -fsSL https://bun.sh/install | bash

# Arch
sudo pacman -S --needed nodejs npm git curl
curl -fsSL https://bun.sh/install | bash

# macOS
brew install node git
curl -fsSL https://bun.sh/install | bash

# Windows
winget install OpenJS.NodeJS Git.Git
irm bun.sh/install.ps1 | iex

# --- Project Setup ---
bun create vue@latest my-vue-app --ts
cd my-vue-app
bun install

# --- Run Dev Server ---
bun dev
"""

REMIX_JS_TEMPLATE="""
# --- Prerequisites check ---
bun --version || echo "Bun not found"
node --version || echo "Node.js not found"
git --version || echo "Git not found"

# --- Installation ---
# Debian/Ubuntu
sudo apt update
sudo apt install -y nodejs npm git curl
curl -fsSL https://bun.sh/install | bash

# Arch
sudo pacman -S --needed nodejs npm git curl
curl -fsSL https://bun.sh/install | bash

# macOS
brew install node git
curl -fsSL https://bun.sh/install | bash

# Windows
winget install OpenJS.NodeJS Git.Git
irm bun.sh/install.ps1 | iex

# --- Project Setup ---
bunx create-remix@latest my-remix-app --typescript
cd my-remix-app
bun install

# --- Run Dev Server ---
bun dev
"""

NEST_JS_TEMPLATE="""
# --- Prerequisites check ---
bun --version || echo "Bun not found"
node --version || echo "Node.js not found"
git --version || echo "Git not found"

# --- Installation ---
# Debian/Ubuntu
sudo apt update
sudo apt install -y nodejs npm git curl
curl -fsSL https://bun.sh/install | bash

# Arch
sudo pacman -S --needed nodejs npm git curl
curl -fsSL https://bun.sh/install | bash

# macOS
brew install node git
curl -fsSL https://bun.sh/install | bash

# Windows
winget install OpenJS.NodeJS Git.Git
irm bun.sh/install.ps1 | iex

# --- Project Setup ---
bun add -g @nestjs/cli
nest new my-nest-app --package-manager bun
cd my-nest-app

# --- Run Dev Server ---
bun start --watch
"""
