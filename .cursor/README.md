# .cursor Documentation

This directory contains consolidated, up-to-date documentation for the MetaMind project, organized for easy access by Cursor AI.

## Documentation Files

- **`.cursorrules`** - Main reference file for Cursor AI (read this first!)
- **`architecture.md`** - System architecture and design patterns
- **`api-reference.md`** - Complete API documentation
- **`features.md`** - Current features and capabilities
- **`development-guide.md`** - Development workflow and guidelines

## Quick Links

### For New Developers
1. Read `.cursorrules` for project overview
2. Follow `development-guide.md` for setup
3. Review `architecture.md` to understand system design
4. Check `features.md` for current capabilities

### For Adding Features
1. Review `architecture.md` for design patterns
2. Follow examples in `development-guide.md`
3. Update `api-reference.md` if adding endpoints
4. Update `features.md` with new capabilities

### For Debugging
1. Check `development-guide.md` → Debugging section
2. Review `architecture.md` → Error Handling Strategy
3. Check logs: `logs/api_server_*.log`
4. Check state: `extracted_meta/progress.json`

## Documentation Principles

- **Single Source of Truth**: `.cursor/` is the canonical documentation location
- **Up-to-Date**: Reflects current implementation (as of latest changes)
- **Comprehensive**: Covers architecture, API, features, and development
- **AI-Friendly**: Structured for easy parsing by Cursor AI

## Other Documentation

- **Main README**: `/home/devuser/sai_dev/metamind/README.md` - User-facing documentation
- **logs/**: Backend logs (timestamped)
- **docs/**: Legacy documentation (may be outdated, refer to `.cursor/` instead)

## Maintenance

When adding new features:
1. Update relevant `.cursor/*.md` files
2. Keep `.cursorrules` summary updated
3. Update main `README.md` if user-facing
4. Remove stale documentation from `docs/`

Last Updated: 2025-11-25
