# Changelog

All notable changes to the Dolibarr MCP Server are documented here. The project
follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html) and adopts the
[Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format.

## [Unreleased]

### Fixed
- Decoding/parsing of Dolibarr API responses now handles gzip payloads robustly in both client implementations (`client/base.py` and legacy `dolibarr_client.py`), including servers that return gzip bytes without `Content-Encoding`.
- `POST /proposals` no longer fails with UTF-8 decode errors when Dolibarr returns compressed responses.

### Changed
- Tool descriptions and agent guidance now clarify proposal creation flow:
  - Use `create_proposal(customer_id=...)` for creation.
  - Use `socid` with `get_customer_proposals(...)` for reads/filtering.
  - Keep `dolibarr_raw_api` as escape hatch only.
- API documentation now explicitly documents compression handling and proposal create requirements.
- Proposal schemas now cover extended offer header fields (payment terms/method, references, delivery/source metadata) and line description aliases (`description` -> `desc`) to reduce unnecessary raw API usage.

## [2.1.0] - 2026-01-27

### Added
- **TOON Format Output**: Token-Oriented Object Notation as default output format
  - ~40% reduction in token usage compared to JSON
  - Self-documenting tabular format: `[N]{field1,field2}:`
  - Automatic fallback to JSON on encoding errors
  - Format selection via `format` parameter (toon, json, json_compact)
- **DragonflyDB Cache**: High-performance async caching layer
  - Compatible with DragonflyDB and Redis (25x faster with DragonflyDB)
  - Entity-specific TTL strategies (30s-1h based on data volatility)
  - Automatic cache invalidation on mutations
  - Graceful degradation when cache unavailable
  - Cache statistics tracking (hits, misses, hit rate)
- **New modules**:
  - `formats/`: TOON encoder and format selection
  - `cache/`: DragonflyDB client and TTL strategies
- **New dispatch functions**:
  - `dispatch_tool_cached()`: Cache-aware tool execution
  - `dispatch_tool_formatted()`: Returns TOON/JSON string output

### Technical Improvements
- Cache strategies per entity type (products=15min, invoices=30s, etc.)
- Automatic cache invalidation map for mutation operations
- Optional `redis` dependency for cache support

## [2.0.0] - 2026-01-27

### Added
- **Modular Architecture**: Complete refactoring into modular structure
  - `client/`: API client with `base.py` and `exceptions.py`
  - `server/`: MCP server with `main.py`, `tools.py`, `handlers.py`, `responses.py`
  - `transports/`: Separated STDIO and HTTP transports
  - `schemas/`: Centralized schema definitions with `base.py`, `fields.py`, `entities.py`
- **Response Wrapper System**: Unified response format with `success_response()`, `error_response()`, `paginated_response()`
- **Enhanced Error Handling**: Structured errors with codes, retriable flags, and correlation IDs
  - `DolibarrAPIError`, `DolibarrValidationError`, `DolibarrNotFoundError`, `DolibarrConnectionError`
- **Dynamic Tool Dispatcher**: Replaced 59 if-statements with declarative `TOOL_REGISTRY` lookup table
- **AI-Optimized Descriptions**: All 59 tools now have detailed descriptions following format:
  `[ACTION] [OBJECT]. [FIELDS RETURNED]. [CONSTRAINTS/NOTES].`
- **Schema Documentation**: Full JSON Schema with descriptions, constraints, and examples

### Changed
- **Token Efficiency**: Responses now include metadata for pagination and debugging
- **Error Responses**: Now include `code`, `message`, `status`, `retriable`, `details`
- **Compatibility**: Backward compatible with existing tests via `dispatch_tool_legacy()`

### Technical Improvements
- Reduced code duplication by ~40%
- Single lookup table for tool dispatch (was 59 if-statements)
- Centralized field filtering definitions
- Cleaner separation of concerns

### Added
- Restored README.md and CHANGELOG.md after merge conflicts while preserving the streamlined structure shared with `prestashop-mcp`.
- Documented platform-specific setup covering Linux/macOS shells, Windows Visual Studio `vsenv`, and the Docker workflow.

### Changed
- Reconciled feature and tool descriptions so they capture both the detailed ERP coverage and the new documentation bundle layout.
- Clarified configuration guidance around `pydantic-settings`, environment variables, and `.env` files.

### Removed
- Obsolete references to legacy helper scripts and superseded documentation variants that were dropped during the repository cleanup.

## [1.1.0]

### Removed
- Legacy helper scripts, installers, and manual test programs that duplicated the automated test-suite.
- Alternative server implementations (`simple_client`, `standalone_server`, `ultra_simple_server`) in favour of the single `dolibarr_mcp_server`.
- Redundant documentation fragments and variant requirements files that no longer reflected the current project layout.

### Changed
- Rewrote the README to highlight the streamlined structure and provide concise installation/run instructions.
- Clarified that `dolibarr_mcp_server.py` is the definitive MCP entry point.

## [1.1.0]

### Removed
- Legacy helper scripts, installers and manual test programs that duplicated the automated test-suite
- Alternative server implementations (`simple_client`, `standalone_server`, `ultra_simple_server`) in favour of the single `dolibarr_mcp_server`
- Redundant documentation fragments and variant requirements files that no longer reflected the current project layout

### Changed
- Rewrote the README to highlight the streamlined structure and provide concise installation/run instructions
- Clarified that `dolibarr_mcp_server.py` is the definitive MCP entry point

## [1.0.0]

### 🎯 Major Restructuring

This release represents a complete restructuring of the Dolibarr MCP Server to match the clean architecture of prestashop-mcp.

### Added
- Professional README.md with comprehensive documentation.
- Structured test suite in `tests/` directory.
- Clean configuration management.
- Docker support for easy deployment.
- Comprehensive CRUD operations for all Dolibarr entities.

### Changed
- Complete repository restructuring to match prestashop-mcp pattern.
- Simplified dependencies in requirements.txt.
- Cleaned up package structure in `src/dolibarr_mcp/`.
- Updated pyproject.toml with proper metadata.
- Streamlined .gitignore file.

### Removed
- Outdated prototype assets from the first public release.

### Technical Improvements
- Single, focused MCP server implementation.
- Clean separation of concerns.
- Better error handling.
- Improved logging.
- Async/await architecture throughout.

## [0.5.0]

### Added
- Initial Dolibarr API integration.
- Basic CRUD operations for customers, products, invoices.
- MCP server implementation.
- Docker configuration.

## [0.1.0]
### Added
- Initial project setup.
- Basic repository structure.
- License and documentation.

---

**Note**: Entries prior to v1.0.0 summarise the historical evolution of the project and are retained for context.
