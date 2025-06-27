# Runtime Bundling & Distribution Issue

## Problem Statement

AWD CLI currently has a fundamental distribution problem that breaks the quickstart experience:

1. **Binary Installation**: `curl install.sh` installs AWD binary (works ✅)
2. **Runtime Dependency**: Quickstart assumes `llm keys set github` works (fails ❌)
3. **Execution Failure**: `awd run` fails because no LLM runtime is available (fails ❌)

**Result**: The "30 seconds" quickstart is broken for users following the binary installation path.

## Current Architecture vs Reality

### What We Promise (README):
```bash
# 1. Install AWD CLI
curl -sSL https://raw.githubusercontent.com/danielmeppiel/awd-cli/main/install.sh | sh

# 2. Setup runtime and configure GitHub Models  
awd runtime setup codex
export GITHUB_TOKEN=your_token_here

# 3. Initialize your first AWD project
awd init my-hello-world

# 4. Install and run
cd my-hello-world
awd install
awd run --param name="Developer"
```

### What Actually Happens:
```bash
# Step 1: ✅ Works
curl -sSL https://raw.githubusercontent.com/danielmeppiel/awd-cli/main/install.sh | sh  # Installs AWD binary

# Step 2: ✅ Works (after implementing runtime management)
awd runtime setup codex  # Downloads codex-rs, creates GitHub Models config
export GITHUB_TOKEN=your_token_here

# Step 4: ✅ Works
awd run --param name="Developer"  # Executes via codex runtime
```

## Architecture Challenge

We want:
- ✅ Standalone binary (no Python dependency for distribution)
- ✅ Works with multiple runtimes (llm, codex, future ones) 
- ✅ Simple installation process
- ✅ Runtime flexibility via adapters
- ✅ AWD manages runtime installation and configuration

**The Solution**: AWD becomes a runtime package manager that handles downloading, installing, and configuring AI runtimes from their official sources.

## How NPM Solved This

**NPM/Node.js Pattern:**
- **Node.js** = Runtime (equivalent to our codex/llm)
- **npm** = Package manager (equivalent to AWD)
- **Solution**: npm comes bundled WITH Node.js, but also manages other tools
- **Result**: Install Node.js → get npm → use npm to manage ecosystem

**AWD Pattern:**
- **Codex/LLM** = Runtime (AI execution engines)
- **AWD** = Package manager + Runtime manager
- **Solution**: AWD manages both prompts AND runtimes
- **Result**: Install AWD → use AWD to install runtimes → run prompts

**Key Insight**: AWD becomes the universal manager for the entire AI development stack.

## Architectural Options

### Option 4: AWD as Runtime Package Manager ⭐ (Recommended)
AWD manages installation and configuration of AI runtimes from their official sources.

**Implementation:**
```bash
# Install AWD binary only
curl -sSL https://raw.githubusercontent.com/danielmeppiel/awd-cli/main/install.sh | sh

# AWD downloads and configures codex-rs from GitHub releases
# This installs Codex rust CLI (documented here https://github.com/openai/codex/tree/main/codex-rs)
awd runtime setup codex  # Downloads from https://github.com/openai/codex/releases

# Set authentication
export GITHUB_TOKEN=your_token_here

# Use immediately
awd init my-project && cd my-project
awd install && awd run --param name="Developer"
```

**Runtime Management:**
```bash
# What `awd runtime setup codex` does:
# 1. Detect platform (linux-x86_64, darwin-x86_64, darwin-arm64)  
# 2. Run embedded setup-codex.sh script
# 3. Script downloads latest codex-rs binary from GitHub releases
# 4. Install to ~/.awd/runtimes/codex
# 5. Create ~/.codex/config.toml with GitHub Models configuration:

mkdir -p ~/.awd/runtimes ~/.codex
curl -L "https://github.com/openai/codex/releases/latest/download/codex-${PLATFORM}" \
     -o ~/.awd/runtimes/codex
chmod +x ~/.awd/runtimes/codex

cat > ~/.codex/config.toml << 'EOF'
model_provider = "github-models"
model = "gpt-4.1"

[model_providers.github-models]
name = "GitHub Models"
base_url = "https://models.github.ai/inference"
env_key = "GITHUB_TOKEN"
wire_api = "chat"
EOF

# Add to PATH if needed
export PATH="$HOME/.awd/runtimes:$PATH"
```

**Runtime Hierarchy:**
```python
RUNTIME_PREFERENCE = [
    "codex",        # Primary runtime (managed by AWD)
    "llm",          # Fallback (also managed by AWD)
]
```

**Extended Runtime Management:**
```bash
awd runtime setup llm                    # Install llm via pip
awd runtime setup codex --version=v1.2.3 # Install specific version
awd runtime list                         # Show installed runtimes
awd runtime update codex                 # Update to latest version
awd runtime remove llm                   # Uninstall runtime
```

**Pros:**
- ✅ Clean separation: AWD binary vs runtime binaries
- ✅ Platform-aware runtime installation
- ✅ Official sources (GitHub releases, pip, etc.)
- ✅ Version management and updates
- ✅ Extensible to any future runtime
- ✅ User controls installation timing

**Cons:**
- ❌ Requires internet for runtime setup
- ❌ Additional step after AWD installation
- ❌ Runtime management complexity

## Recommendation: Option 4 (AWD as Runtime Package Manager)

**Why:** This transforms AWD into a universal AI development platform manager while maintaining clean separation of concerns.

### Implementation Plan:

1. **Enhanced Installation Script:**
   ```bash
   # install.sh downloads and installs AWD binary only
   curl -sSL https://raw.githubusercontent.com/danielmeppiel/awd-cli/main/install.sh | sh
   ```

2. **Runtime Package Manager Interface (Embedded Scripts):**
   ```python
   class RuntimeManager:
       def setup_codex(self, version=None):
           # 1. Detect platform (linux-x86_64, darwin-x86_64, darwin-arm64)
           # 2. Run embedded setup-codex.sh script
           # 3. Script downloads from https://github.com/openai/codex/releases
           # 4. Install to ~/.awd/runtimes/codex
           # 5. Create ~/.codex/config.toml with GitHub Models + gpt-4.1
           platform = self.detect_platform()
           script = self.get_embedded_script("setup-codex.sh")
           self.run_bash_script(script, platform=platform, version=version)
           
       def setup_llm(self):
           # Run embedded setup-llm.sh script
           # Install llm via pip in managed environment
           script = self.get_embedded_script("setup-llm.sh") 
           self.run_bash_script(script)
   ```

3. **Updated Quickstart:**
   ```bash
   # 1. Install AWD
   curl -sSL https://raw.githubusercontent.com/danielmeppiel/awd-cli/main/install.sh | sh
   
   # 2. Setup runtime (AWD handles download and config)
   awd runtime setup codex
   
   # 3. Set authentication
   export GITHUB_TOKEN=your_token_here
   
   # 4. Use immediately
   awd init my-project && cd my-project
   awd install && awd run --param name="Developer"
   ```

4. **Preserve Flexibility:**
   ```bash
   # Advanced users can still manage manually or use different runtimes
   awd runtime setup llm              # AWD-managed llm
   awd run --runtime=codex            # Use codex
   awd run --runtime=llm              # Use llm
   ```

## Next Steps

1. **Create embedded setup scripts** (`scripts/setup-codex.sh`, `scripts/setup-llm.sh`)
2. **Implement `awd runtime` command infrastructure** with embedded script execution
3. **Add platform detection** matching build-release.yml (linux-x86_64, darwin-x86_64, darwin-arm64)
4. **Integrate scripts into PyInstaller build** to embed in AWD binary
5. **Test cross-platform runtime installation** using embedded scripts
6. **Update documentation** to reflect bash script-based runtime management

**Platform Support**: Target same platforms as current build pipeline:
- `linux-x86_64` (Ubuntu 22.04)
- `darwin-x86_64` (macOS 13 Intel) 
- `darwin-arm64` (macOS 14 Apple Silicon)

This approach leverages your existing robust build infrastructure while providing transparent, maintainable runtime management through embedded bash scripts.
