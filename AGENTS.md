# Agent Instructions

## Tooling
  - Always use commands from makefiles when available
  - Create/use Makefiles as the entry point for commands for CI/CD, tests, linting, setup, etc
    - Use targets "setup" (tool preparation), "install" (deps install), "build" (package preparation), "test" (unit tests), "lint" (type, format, code and audit checks), "run" (local run during dev), "deploy" (deploy to cloud), "undeploy" and "all" (calls build, test, lint)
    - Add commands to Makefiles as needed (such as utilities etc), but only commands that would be reused more often
  - Use Makefiles, Python, uv, RUFF, Mypy, Pytest, Fastapi, Pydantic and LangChain
  - Store keys in OSXKeychain for local run and receive as ENV variables during deployment
  
## Quality
  - Create unit tests for new features and bug fixes, and ensure all tests pass
  - Run "make all" everytime you make changes to ensure lint, test and build is working fine. Fix any issues.
  - Always run the commands or features you are creating or modifying to ensure they work as expected and fix any issues

## Conventions
  - Use .test in file name for tests, instead of .spec

