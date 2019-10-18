/**
 * Logging functions and variables
 * 
 * Copyright (c) 2019 Contributors to the openHAB Scripters project
 * 
 * @author Martin Stangl - initial contribution
 */
'use strict';	

(function context (context) {
    'use strict';	
    
    load(__DIR__+'/actions.js');        

    context.NOTIFY_OFF = 0;
    context.NOTIFY_ERROR = 200;
    context.NOTIFY_WARN = 300;
    context.NOTIFY_INFO = 400;
    context.NOTIFY_DEBUG = 500;

    context.Logger = function Logger (name, notificationLevel, config) {        
        if (name === undefined) {
            name = Error().stack.split('\n')[2].split('/').slice(-2).join('.').split(':')[0];
            name = name.slice(-3) == ".js" ? name.slice(0,-3) : null;
        }
        var _logger  = Java.type("org.slf4j.LoggerFactory").getLogger(name === null ? "jsr223.javascript" : "jsr223.javascript." + name.toString().toLowerCase());        

        try {
            // Set default config for config params not provided.
            if (config === undefined) config = {};
            if (config.ERROR === undefined) config.ERROR = {};
            if (config.WARN  === undefined) config.WARN  = {};
            if (config.INFO  === undefined) config.INFO  = {};
            if (config.DEBUG === undefined) config.DEBUG = {};
            if (config.ERROR.prefix === undefined) config.ERROR.prefix = "short";
            if (config.WARN.prefix  === undefined) config.WARN.prefix  = "none";
            if (config.INFO.prefix  === undefined) config.INFO.prefix  = "none";
            if (config.DEBUG.prefix === undefined) config.DEBUG.prefix = "short";       

            return Object.create(Object.prototype, {
                _notificationLevel: { value: (notificationLevel === undefined || notificationLevel === null) ? context.NOTIFY_OFF : notificationLevel },
                _config: { value: config },                
                _name: { value: name },

                error: { value: function error (msg) {
                    try {
                        if (_logger.isErrorEnabled()) {                      
                            eval("_logger.error" + this._loggerArgs(this._getLogMessage(msg), arguments.length));                        
                        }
                        if (this._notificationLevel >= context.NOTIFY_ERROR) {
                            this._sendNotification(this._getLogMessage(msg, this._config.ERROR.prefix, "ERROR"), "fire", "ERROR");
                        }
                    } catch (err) {
                        _logger.error(this._getLogMessage(err));
                    }
                }},              

                warn: { value: function warn (msg) {
                    try {
                        if (_logger.isWarnEnabled()) {                      
                            eval("_logger.warn" + this._loggerArgs(this._getLogMessage(msg), arguments.length));                        
                        }
                        if (this._notificationLevel >= context.NOTIFY_WARN) {
                            this._sendNotification(this._getLogMessage(msg, this._config.WARN.prefix, "WARN"), "error", "WARN");                            
                        }
                    } catch (err) {
                        _logger.error(this._getLogMessage(err));
                    }
                }},

                info: { value: function info (msg) {
                    try {
                        if (_logger.isInfoEnabled()) {                      
                            eval("_logger.info" + this._loggerArgs(this._getLogMessage(msg), arguments.length));                        
                        }
                        if (this._notificationLevel >= context.NOTIFY_INFO) {
                            this._sendNotification(this._getLogMessage(msg, this._config.INFO.prefix, "INFO"), "lightbulb", "INFO");                            
                        }
                    } catch (err) {
                        _logger.error(this._getLogMessage(err));
                    }
                }},

                debug: { value: function debug (msg) {
                    try {
                        if (_logger.isDebugEnabled()) {                      
                            eval("_logger.debug" + this._loggerArgs(this._getLogMessage(msg), arguments.length));                        
                        }
                        if (this._notificationLevel >= context.NOTIFY_DEBUG) {
                            this._sendNotification(this._getLogMessage(msg, this._config.DEBUG.prefix, "DEBUG"), "text", "DEBUG");                            
                        }
                    } catch (err) {
                        _logger.error(this._getLogMessage(err));
                    }
                }},

                trace: { value: function trace (msg) {
                    try {                        
                        if (_logger.isTraceEnabled()) {                      
                            eval("_logger.trace" + this._loggerArgs(this._getLogMessage(msg), arguments.length));                        
                        }
                    } catch (err) {                        
                        _logger.error(this._getLogMessage(err));                        
                    }
                }},

                _getCaller: { value: function _getCaller (stack) {
                    try {                                                              
                        return stack.split('\n\tat ')[1].split(' ')[0];
                    } catch (err) {
                        return null;
                    }
                }},

                _getLogMessage: { value: function _getLogMessage (msg, prefix, levelString) {                                        
                    msg = this._legacyLoggerCorrection(msg);

                    if (prefix === undefined) prefix = "log";                                                            
                    
                    if (prefix == "none") {
                        return msg.message;
                    }

                    var level = "";
                    var name = "";
                    if (prefix != "log") {
                        level = "[" + levelString + "] ";
                        name = this._name === null ? "" : this._name + ": ";
                    }

                    if (prefix == "level") {
                        return (level + msg.message);
                    }

                    var caller = this._getCaller(msg.stack);
                    var callerText;
                    if (caller === null) {
                        callerText = "";
                    } else if (caller.substr(0,1) == "<") {
                        callerText = ", in " + caller;
                    } else {
                        callerText = ", function " + caller;
                    }
                    var message = msg.message == "" ? "" : "] " + msg.message;                    

                    if (prefix == "short") {
                        return (level + "[" + name + msg.fileName.split('/').pop() + ":" + msg.lineNumber + callerText + message);    
                    }

                    return (level + "[" + name + "source " + msg.fileName + ", line " + msg.lineNumber + callerText + message);
                }},
                
                _legacyLoggerCorrection: { value: function _legacyLoggerCorrection (msg) {
                    if (msg.fileName.search(/automation\/lib\/javascript\/core\/utils\.js$/) !== -1) {
                        switch (this._getCaller(msg.stack)) {
                            case "logError":
                            case "logWarn":
                            case "logInfo":
                            case "logDebug":
                            case "logTrace":  
                            case "log":                              
                                msg.stack = msg.stack.split('\n\tat ').slice(1).join('\n\tat ');
                                msg.fileName = msg.stack.split('\n\tat ')[1].match(/.*? \((.*):/)[1];
                                msg.lineNumber = msg.stack.split('\n\tat ')[1].match(/.*:(.*?)\)/)[1];                                
                        }
                    }
                    return msg;
                }},

                _sendNotification: { value: function _sendNotification (message, icon, levelString) {                                                                                
                    if (this._config[levelString].recipients !== undefined) {
                        this._config[levelString].recipients.forEach(function(mail){             
                            NotificationAction.sendNotification(mail, message, icon, levelString);                            
                        })
                        if (this._config[levelString].recipients.length > 0) {
                            this.trace(Error("Notification sent to " + this._config[levelString].recipients.join(", ") + ". Message: \"" + message + "\""));
                        }                         
                    } else {                        
                        NotificationAction.sendBroadcastNotification(message, icon, levelString);
                        this.trace(Error("Broadcast notification sent. Message: \"" + message + "\""));
                    }                    
                }},

                _loggerArgs: { value: function _loggerArgs (msg, length) {                    
                    var str = "(\"" + msg.replace(/\n/g, '\\n') + "\"";
                    for (var i = 1; i < length; i++) {
                        str = str+",arguments["+i+"]";
                    }    
                    str = str+");"                                              
                    return str;
                }}

            })
        } catch (err) {
            _logger.error(err.fileName + ", line " + err.lineNumber + ": " + err.message);
        }
    }    

})(this);