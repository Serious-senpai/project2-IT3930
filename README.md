[![Azure deployment](https://github.com/Serious-senpai/project2-IT3930/actions/workflows/deploy.yml/badge.svg)](https://github.com/Serious-senpai/project2-IT3930/actions/workflows/deploy.yml)
[![Lint](https://github.com/Serious-senpai/project2-IT3930/actions/workflows/lint.yml/badge.svg)](https://github.com/Serious-senpai/project2-IT3930/actions/workflows/lint.yml)

## API documentation

### Permissions

Permissions are a way to limit and grant certain abilities to users. For long-term stability, it's recommended to deserialize the permissions using your preferred languages' Big Integer libraries. The total permissions integer can be determined by OR-ing (`|`) together each individual value, and flags can be checked using AND (`&`) operations.

| PERMISSION | VALUE | DESCRIPTION |
| ---------- | ----- | ----------- |
| **ADMINISTRATOR** | `0x1 (1 << 0)` | Allow all permissions |
| **VIEW_USERS** | `0x2 (1 << 1)` | Allow viewing information of users, including vehicles, violations, etc. (without this permission, users can only view data related to themselves) |
| **CREATE_VEHICLE** | `0x4 (1 << 2)` | Allow registering vehicles for other users (without this permission, users can only register vehicles for themselves) |
| **CREATE_VIOLATION** | `0x8 (1 << 3)` | Allow creating new violations |
| **CREATE_REFUTATION** | `0x16 (1 << 4)` | Allow creating new refutations of violations for other users (without this permission, users can only create a refutation for themselves) |
