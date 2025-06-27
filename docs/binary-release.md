# Binary Release Process

This document describes how to create and publish AWD CLI binary releases.

## Prerequisites

1. **Push all changes** to the main branch
2. **Test locally** that everything works
3. **Update version** in `pyproject.toml` if needed

## Creating a Release

### 1. Create and Push a Tag

```bash
# Create a version tag
git tag v0.1.0

# Push the tag to GitHub
git push origin v0.1.0
```

### 2. Create GitHub Release

1. Go to [GitHub Releases](https://github.com/danielmeppiel/awd-cli/releases)
2. Click **"Draft a new release"**
3. Choose the tag you just created (e.g., `v0.1.0`)
4. Fill in the release information:
   - **Release title**: `AWD CLI v0.1.0`
   - **Description**: Add release notes, features, bug fixes, etc.
5. Click **"Publish release"**

### 3. Automatic Binary Building

Once you publish the release, GitHub Actions will automatically:

1. ✅ Build binaries for:
   - `awd-linux-x86_64` (Linux 64-bit)
   - `awd-darwin-x86_64` (macOS Intel)
   - `awd-darwin-arm64` (macOS Apple Silicon)

2. ✅ Generate SHA256 checksums for each binary

3. ✅ Upload binaries and checksums to the GitHub Release

4. ✅ Test each binary to ensure it works

This process takes about 5-10 minutes.

## Download URLs

After the release is published and binaries are built, users can download:

### Direct Downloads
```bash
# Linux
curl -L https://github.com/danielmeppiel/awd-cli/releases/latest/download/awd-linux-x86_64 -o awd

# macOS Intel  
curl -L https://github.com/danielmeppiel/awd-cli/releases/latest/download/awd-darwin-x86_64 -o awd

# macOS Apple Silicon
curl -L https://github.com/danielmeppiel/awd-cli/releases/latest/download/awd-darwin-arm64 -o awd
```

### Install Script (Recommended)
```bash
curl -sSL https://raw.githubusercontent.com/danielmeppiel/awd-cli/main/install.sh | sh
```

The install script automatically:
- Detects the user's platform (OS + architecture)
- Downloads the correct binary
- Installs to `/usr/local/bin/awd`
- Makes the binary executable
- Verifies the installation

## Local Binary Building

To build binaries locally for testing:

```bash
# Install build dependencies
pip install -e ".[build]"

# Build binary for current platform
./scripts/build-binary.sh

# Test the binary
./dist/awd-$(uname -s | tr '[:upper:]' '[:lower:]')-$(uname -m) --version
```

## Binary Details

- **Size**: ~10-15MB (compressed with UPX)
- **Dependencies**: None (fully self-contained)
- **Templates**: Bundled inside the binary
- **Startup time**: < 1 second
- **Platforms**: Linux x86_64, macOS x86_64, macOS ARM64

## Troubleshooting

### Build Fails
- Check GitHub Actions logs for detailed error messages
- Ensure all Python dependencies are correctly specified
- Verify PyInstaller spec file is correct

### Binary Doesn't Work
- Check that templates are being bundled correctly
- Verify the entry point and module imports
- Test locally with the same build process

### Users Can't Download
- Ensure the release is published (not draft)
- Check that GitHub Actions completed successfully
- Verify download URLs are correct

## Release Checklist

Before creating a release:

- [ ] All tests pass
- [ ] Documentation is updated
- [ ] Version number is bumped in `pyproject.toml`
- [ ] Changes are documented in release notes
- [ ] Local binary build works
- [ ] Templates and functionality work in binary

After creating a release:

- [ ] GitHub Actions completed successfully
- [ ] All 3 binaries are attached to the release
- [ ] Install script works with new release
- [ ] Binaries can be downloaded and executed
- [ ] Release notes are accurate

## Future Improvements

1. **Windows Support**: Add Windows binary builds
2. **Package Managers**: Create Homebrew formula, APT packages
3. **Auto-updater**: Add `awd update` command
4. **Compression**: Further optimize binary size
5. **Code Signing**: Sign binaries for macOS/Windows
