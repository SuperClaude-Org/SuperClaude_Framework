# Dynamic-Use Checklist

## Purpose
Before classifying ANY file as DELETE, agents must check all 5 dynamic loading patterns below. "No imports found" via static grep is insufficient when dynamic loading is used.

## Instruction
**Check ALL 5 patterns before classifying a file as DELETE.** If any pattern could load the file, classify as REVIEW instead.

## Pattern 1: Environment Variable-Based Module Loading

Files loaded based on environment variable values at runtime.

**JavaScript/Node.js**:
```javascript
const module = require(process.env.MODULE_PATH);
const handler = await import(`./handlers/${process.env.HANDLER_TYPE}`);
```

**Python**:
```python
module = importlib.import_module(os.environ.get('PLUGIN_MODULE'))
handler = __import__(os.getenv('HANDLER_CLASS'))
```

**Check**: Search for `process.env`, `os.environ`, `os.getenv` near import/require/load statements.

## Pattern 2: String-Based Import Loaders

Files loaded by constructing import paths from string variables.

**JavaScript/Node.js**:
```javascript
const plugin = require(`./plugins/${pluginName}`);
const component = await import(`@/components/${name}.vue`);
```

**Python**:
```python
module = importlib.import_module(f"app.handlers.{handler_name}")
cls = getattr(importlib.import_module(module_path), class_name)
```

**Check**: Search for template literals in imports, `importlib.import_module` with variables, `__import__` with variables.

## Pattern 3: Plugin Registries

Files registered in a configuration and loaded on demand.

**JavaScript**:
```javascript
// config/plugins.json
{ "plugins": ["analytics", "auth", "logging"] }
// Loader reads config and requires each
plugins.forEach(p => require(`./plugins/${p}`));
```

**Python**:
```python
# entry_points in pyproject.toml or setup.cfg
[options.entry_points]
my_plugins =
    auth = myapp.plugins.auth:AuthPlugin
```

**Check**: Search for plugin/extension/addon configuration files. Check `entry_points`, plugin manifests, registry patterns.

## Pattern 4: Glob-Based File Discovery

Files discovered at runtime via filesystem glob patterns.

**JavaScript/Node.js**:
```javascript
const routes = glob.sync('./routes/**/*.js');
const migrations = fs.readdirSync('./migrations').filter(f => f.endsWith('.sql'));
```

**Python**:
```python
for path in Path('handlers').glob('*.py'):
    importlib.import_module(f"handlers.{path.stem}")
```

**Go**:
```go
files, _ := filepath.Glob("./templates/*.tmpl")
```

**Check**: Search for `glob`, `readdirSync`, `readdir`, `Path.glob`, `filepath.Glob`, `os.listdir` patterns that load files from the target directory.

## Pattern 5: Config-Driven Loading Patterns

Files referenced in configuration that is parsed at runtime.

**Examples**:
```yaml
# webpack.config.js entry points
entry: { app: './src/app.js', vendor: './src/vendor.js' }

# pytest.ini / setup.cfg
testpaths = tests extra_tests legacy_tests

# tsconfig.json paths
"paths": { "@utils/*": ["src/utils/*"] }
```

**Check**: Search config files (`*.config.*`, `*.json`, `*.yaml`, `*.toml`, `*.ini`) for path references that could load the target file.

## Summary Checklist

Before every DELETE classification:

- [ ] **Pattern 1**: No env-var-based loading references the file
- [ ] **Pattern 2**: No string-constructed imports reference the file
- [ ] **Pattern 3**: No plugin registry includes the file
- [ ] **Pattern 4**: No glob/readdir pattern discovers the file
- [ ] **Pattern 5**: No config file references the file path

If ANY check is uncertain, classify as **REVIEW** instead of DELETE.
