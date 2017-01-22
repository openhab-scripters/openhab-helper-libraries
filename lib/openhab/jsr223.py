import sys
import types

class Jsr223ModuleFinder(object):
    class ScopeModule(types.ModuleType):
        @staticmethod
        def _get_jsr223_scope():
            depth = 1
            while True:
                try:
                    frame = sys._getframe(depth)
                    name = str(type(frame.f_globals))
                    if name == "<type 'scope'>":
                        return frame.f_globals
                    depth += 1
                except ValueError:
                    raise EnvironmentError("No JSR223 scope is available")
                
        def __getattr__(self, name):
            scope = self._get_jsr223_scope()
            if name == "scope":
                return scope
            elif name == "HandlerRegistry":
                scope.get("ScriptExtension").importPreset("RuleSupport")
                return scope.get("HandlerRegistry")
            return scope.get(name, None) or getattr(scope, name, None)
    
    def load_module(self, fullname):
        if fullname not in sys.modules:
            m = Jsr223ModuleFinder.ScopeModule('scope')
            setattr(m , '__file__', '<jsr223>')
            setattr(m , '__name__', 'scope')
            setattr(m , '__loader__', self)
            sys.modules[fullname] = m
                
    def find_module(self, fullname, path=None):
        if fullname == "openhab.jsr223.scope":
            return self
        
sys.meta_path.append(Jsr223ModuleFinder())

