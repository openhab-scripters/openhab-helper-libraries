from org.slf4j import Logger, LoggerFactory

ScriptExtension.importPreset("RuleSupport")

class LoggerAction(ActionHandler):
    def __init__(self, module):
        self.module = module

    def dispose(self):
        pass

    def execute(self, context):
        config = self.module.configuration
        logger = LoggerFactory.getLogger(config.get('logname'))
        logger.info(str(config.get('message')))
        return {"result": "success"}

def param(name, type, label, default=None, required=False):
    return ConfigDescriptionParameterBuilder.create(name, type)\
        .withLabel(label).withDefault(default).withRequired(required).build()
        
automationManager.addActionHandler("LogAction", lambda module: LoggerAction(module))

automationManager.addActionType(ActionType(
    "LogAction", 
    [
        param("logname", ConfigDescriptionParameter.Type.TEXT, "Logger Name", default="LogAction"),
        param("message", ConfigDescriptionParameter.Type.TEXT, "Message", required=True)
    ],
    "write a log record",
    "Write a record to the log file.",
    set(),  Visibility.VISIBLE, [], []))