---
description: When adding,editing, designing python code
globs: 
alwaysApply: false
---

# Python Development AI Code Assistant Guidelines

## Core Expertise
- **Python Development**: Master Python syntax, semantics, language features, and evolution across versions
- **Project Architecture**: Design scalable, maintainable architecture patterns appropriate to project scope
- **Testing Strategies**: Implement comprehensive testing methodologies across all system levels
- **Code Quality**: Enforce style, readability, and technical debt management standards
- **Package Management**: Handle dependencies safely, securely, and efficiently using uv
- **Performance Optimization**: Identify and resolve bottlenecks using appropriate profiling tools
- **Security Best Practices**: Implement security by design in all code recommendations

## Development Guidelines

### 1. Project Structure
**ALWAYS:**
- Use proper package layout with `src/` directory for production code
- Separate package code from deployment configuration
- Follow Python's established package structure (setup.py/pyproject.toml, README, etc.)
- Store configuration in environment variables or dedicated config files (not hardcoded)
- Implement clean separation between interface and implementation
- Use namespaces appropriately to organize code
- Create comprehensive documentation including architecture diagrams
- Separate business logic from infrastructure code

**NEVER:**
- Mix package boundaries or create circular dependencies
- Skip project structure planning for "quick" implementations
- Ignore Python packaging standards (PEP 517/518)
- Use flat structure for complex applications
- Hardcode environment-specific values
- Duplicate functionality across modules
- Mix test and production code in the same directories

**RECOMMENDED STRUCTURE:**
```
project_name/
├── .github/              # GitHub specific files (actions, templates)
├── docs/                 # Documentation files
├── src/                  # Source directory
│   └── package_name/     # Main package directory
│       ├── __init__.py   # Package initialization
│       ├── module1.py    # Core modules
│       ├── module2.py
│       └── subpackage/   # Subpackages as needed
│           └── __init__.py
├── tests/                # Test directory
│   ├── conftest.py       # pytest configuration
│   ├── test_module1.py   # Tests matching the src structure
│   └── test_module2.py
├── .gitignore            # Git ignore file
├── .pre-commit-config.yaml  # Pre-commit hooks
├── pyproject.toml        # Project metadata and dependencies
├── README.md             # Project overview
└── tox.ini               # Tox configuration
```

### 2. Code Organization
**ALWAYS:**
- Use explicit imports (avoid `from module import *`)
- Group imports by standard library, third-party, and local
- Implement separation of concerns and clean architecture principles
- Apply SOLID principles (especially Single Responsibility)
- Use type hints consistently (PEP 484)
- Document public APIs with docstrings following established formats (Google, NumPy, etc.)
- Create classes and functions with single, clear responsibilities
- Implement proper error handling with descriptive exceptions
- Use consistent naming conventions across the codebase
- Keep functions focused and under 50 lines where possible
- Follow the Dependency Inversion Principle using abstraction

**NEVER:**
- Create circular imports between modules
- Mix responsibilities within classes or functions
- Skip type annotations on public interfaces
- Write undocumented public APIs
- Use overly generic exception handlers (e.g., bare `except:`)
- Use inconsistent naming styles
- Create monolithic classes with multiple responsibilities
- Use global state when avoidable
- Write excessively complex functions (high cyclomatic complexity)
- Pass too many parameters to functions (>5 is a smell)

### 3. Dependency Management
**ALWAYS:**
- Use uv for dependency management and virtual environments
- Pin dependencies with specific versions for reproducible builds
- Separate production and development dependencies
- Use uv's lock files for deterministic installations
- Regularly update dependencies for security patches
- Specify minimum Python version compatibility
- Consider dependency footprint and impact
- Use dependency groups (prod, dev, test) when available with uv
- Document dependency purposes and constraints
- Check for vulnerability reports in dependencies
- Leverage uv's faster package resolution and installation capabilities

**NEVER:**
- Mix environment dependencies across projects
- Use global package installations for project dependencies
- Skip version pinning ("install latest")
- Ignore security updates for extended periods
- Use deprecated packages without migration plans
- Add unnecessary dependencies when stdlib provides alternatives
- Pin to Python version-specific features without clear documentation
- Use unmaintained packages for crucial functionality
- Use slower dependency managers when uv is available

### 4. Testing Strategy
**ALWAYS:**
- Write comprehensive unit tests with high coverage
- Implement integration tests for component interactions
- Create end-to-end tests for critical paths
- Use appropriate fixtures and mocks
- Test edge cases and error conditions
- Measure and maintain test coverage (aim for >80%)
- Write parametrized tests for similar test cases
- Keep tests independent and deterministic
- Include performance tests for critical paths
- Test asynchronous code properly
- Create separate test environments for different test types
- Include both positive and negative test cases

**NEVER:**
- Skip test documentation explaining test purpose
- Mix test types inappropriately
- Write tests dependent on external services without proper mocking
- Ignore test isolation principles
- Skip testing error scenarios and edge cases
- Create non-deterministic tests
- Test implementation details rather than behavior
- Create overly complex test setups
- Ignore test failures or flaky tests
- Mock what you don't own

## 5. Code Quality
**ALWAYS:**
- Use linting tools (flake8, pylint) with appropriate configuration
- Implement consistent formatting (black, yapf)
- Follow established style guides (PEP 8)
- Employ static type checking (mypy)
- Monitor and limit cyclomatic complexity
- Use pre-commit hooks to enforce standards
- Refactor code when complexity increases
- Perform code reviews with clear criteria
- Use descriptive variable and function names
- Add comments explaining "why" not "what"
- Keep functions and methods focused on single tasks
- Check for and eliminate dead code

**NEVER:**
- Disable linters without documented reasons
- Mix code styles within a project
- Accept increasing complexity without refactoring
- Skip static analysis in the development workflow
- Use cryptic variable names or excessive abbreviations
- Write comments explaining obvious code
- Allow code duplication across the codebase
- Ignore code smells and technical debt
- Use magic numbers without constants or explanations

## 6. Documentation
**ALWAYS:**
- Write clear docstrings for all public APIs
- Maintain comprehensive README with installation and usage instructions
- Document APIs with examples and type information
- Include architecture diagrams for complex systems
- Keep documentation synchronized with code changes
- Document design decisions and trade-offs
- Provide troubleshooting guides for common issues
- Include performance characteristics for critical components
- Document environment requirements and setup
- Provide migration guides for breaking changes

**NEVER:**
- Leave public interfaces undocumented
- Allow documentation to become outdated
- Skip examples for complex functionality
- Omit failure modes and error handling from documentation
- Use unclear terminology in documentation
- Assume users understand implementation details
- Skip documenting configuration options
- Neglect to update documentation during refactoring



## 8. Performance Considerations
**ALWAYS:**
- Profile code before optimization
- Use appropriate data structures for operations
- Consider time and space complexity
- Implement caching for expensive operations
- Optimize database queries and connections
- Use async operations when I/O bound
- Implement proper pagination for large data sets
- Be mindful of memory usage
- Consider horizontal vs. vertical scaling needs
- Use appropriate serialization formats

**NEVER:**
- Optimize prematurely without profiling
- Use inefficient algorithms for performance-critical paths
- Ignore database query performance
- Load entire datasets when pagination is possible
- Block I/O operations unnecessarily
- Create memory leaks with improper resource management
- Ignore performance degradation over time

## 9. Security Best Practices
**ALWAYS:**
- Validate and sanitize all inputs
- Use parameterized queries for databases
- Implement proper authentication and authorization
- Store secrets securely (not in code)
- Apply the principle of least privilege
- Use HTTPS for all network communications
- Implement proper error handling without leaking information
- Keep dependencies updated for security patches
- Use content security policies
- Apply proper file permissions
- Sanitize and validate all file operations

**NEVER:**
- Store credentials in code repositories
- Use SQL string concatenation
- Disable security features for convenience
- Return sensitive data in error messages
- Use weak cryptographic algorithms
- Trust user input without validation
- Expose detailed exception information to users
- Ignore security advisories



## 11. API Design
**ALWAYS:**
- Design consistent, intuitive interfaces
- Follow REST principles for web APIs
- Provide clear error responses
- Version APIs appropriately
- Document all endpoints and parameters
- Implement proper rate limiting
- Design for backward compatibility
- Use appropriate status codes
- Implement pagination for large collections
- Create comprehensive API documentation with examples

**NEVER:**
- Change API behavior without versioning
- Use inconsistent naming conventions
- Return inconsistent data structures
- Skip input validation
- Expose internal implementation details
- Design overly complex interfaces
- Ignore API security considerations

## 12. Error Handling
**ALWAYS:**
- Create custom exception hierarchies for different error types
- Provide meaningful error messages
- Log exceptions with context information
- Handle expected error conditions gracefully
- Implement proper cleanup in finally blocks
- Use context managers for resource management
- Design for fault tolerance
- Return actionable error information to users
- Document error conditions and recovery options

**NEVER:**
- Use bare except clauses
- Silently ignore exceptions
- Return inconsistent error formats
- Leak sensitive information in error messages
- Re-raise exceptions without adding context
- Mix business logic and error handling
- Throw generic exceptions when specific ones would be clearer

## Remember
- **Maintainability** is paramount - code is read more than written
- **Consistency** in style and patterns makes codebases more navigable
- **Testability** should be designed from the beginning
- **Documentation** is a force multiplier for development teams
- **Security** cannot be added as an afterthought
- **Performance** should be measured, not assumed
- **Simplicity** is usually better than clever solutions
- **Modularity** enables easier maintenance and evolution
- **Dependency management** with uv ensures faster and more reliable builds

Ensure the AI code assistant adheres to these guidelines to foster effective Python development, producing code that is not just functional but also maintainable, secure, and aligned with industry best practices.