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
        var _messageFormatter = Java.type("org.slf4j.helpers.MessageFormatter");

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
                            _logger.error(this._getLogMessage(msg), [].slice.call(arguments).slice(1));
                        }
                        if (this._notificationLevel >= context.NOTIFY_ERROR) {
                            this._sendNotification(_messageFormatter.arrayFormat(this._getLogMessage(msg, this._config.ERROR.prefix, "ERROR"), [].slice.call(arguments).slice(1)).getMessage(), "fire", "ERROR");
                        }
                    } catch (err) {
                        _logger.error(this._getLogMessage(err));
                    }
                }},              

                warn: { value: function warn (msg) {
                    try {
                        if (_logger.isWarnEnabled()) {                      
                            _logger.warn(this._getLogMessage(msg), [].slice.call(arguments).slice(1));
                        }
                        if (this._notificationLevel >= context.NOTIFY_WARN) {
                            this._sendNotification(_messageFormatter.arrayFormat(this._getLogMessage(msg, this._config.WARN.prefix, "WARN"), [].slice.call(arguments).slice(1)).getMessage(), "error", "WARN");
                        }
                    } catch (err) {
                        _logger.error(this._getLogMessage(err));
                    }
                }},

                info: { value: function info (msg) {
                    try {
                        if (_logger.isInfoEnabled()) {                      
                            _logger.info(this._getLogMessage(msg), [].slice.call(arguments).slice(1));
                        }
                        if (this._notificationLevel >= context.NOTIFY_INFO) {
                            this._sendNotification(_messageFormatter.arrayFormat(this._getLogMessage(msg, this._config.INFO.prefix, "INFO"), [].slice.call(arguments).slice(1)).getMessage(), "lightbulb", "INFO");
                        }
                    } catch (err) {
                        _logger.error(this._getLogMessage(err));
                    }
                }},

                debug: { value: function debug (msg) {
                    try {
                        if (_logger.isDebugEnabled()) {                      
                            _logger.debug(this._getLogMessage(msg), [].slice.call(arguments).slice(1));
                        }
                        if (this._notificationLevel >= context.NOTIFY_DEBUG) {
                            this._sendNotification(_messageFormatter.arrayFormat(this._getLogMessage(msg, this._config.DEBUG.prefix, "DEBUG"), [].slice.call(arguments).slice(1)).getMessage(), "text", "DEBUG");
                        }
                    } catch (err) {
                        _logger.error(this._getLogMessage(err));
                    }
                }},

                trace: { value: function trace (msg) {
                    try {                        
                        if (_logger.isTraceEnabled()) {     
                            _logger.trace(this._getLogMessage(msg), [].slice.call(arguments).slice(1));                 
                        }
                    } catch (err) {                        
                        _logger.error(this._getLogMessage(err));                        
                    }
                }},
                
                _getCallerDetails: { value: function _getCallerDetails (msg) {
                    var matches = msg.stack.split('\n\tat ')[3].match(/(.+?) \((.+):(\d+?)\)/);
                    msg.caller = matches[1];
                    msg.fileName = matches[2]
                    msg.lineNumber = matches[3]   
                    return msg;
                }},       
                
                _getLogMessage: { value: function _getLogMessage (msg, prefix, levelString) {                                        
                    if ((typeof msg) !== "object") {
                        msg = Error(msg);
                        msg = this._getCallerDetails(msg);
                    } else {
                        msg.caller = msg.stack.split('\n\tat ')[1].split(' (')[0]
                    }
                    msg = this._legacyLoggerCorrection(msg);

                    if (prefix === undefined) prefix = "log";                                                            
                    
                    if (prefix == "none") {
                        return msg.message;
                    }

                    var level = "";
                    var name = "";
                    if (prefix != "log") {
                        level = "[" + levelString + "] ";
                        name = this._name === null ? "" : this._name;
                    }

                    if (prefix == "level") {
                        return (level + msg);
                    }

                    var callerText;
                    if (msg.caller.substr(0,1) == "<") {
                        callerText = ", in " + msg.caller;
                    } else {
                        callerText = ", function " + msg.caller;
                    }
                    
                    var message = msg.message == "" ? "" : "] " + msg.message;                    

                    if (prefix == "short") {
                        return (level + "[" + (name != "" ? name + ", " : "") + msg.fileName.split('/').pop() + ":" + msg.lineNumber + callerText + message);    
                    }
                    return (level + "[" + (name != "" ? name + ": " : "") + "source " + msg.fileName + ", line " + msg.lineNumber + callerText + message);
                }},
                
                _legacyLoggerCorrection: { value: function _legacyLoggerCorrection (msg) {
                    if (msg.fileName.search(/automation\/lib\/javascript\/core\/utils\.js$/) !== -1) {
                        switch (msg.caller) {
                            case "logError":
                            case "logWarn":
                            case "logInfo":
                            case "logDebug":
                            case "logTrace":
                            case "error":
                            case "warn":
                            case "info":
                            case "debug":
                            case "log":
                                var stackArray = msg.stack.split('\n\tat ');
                                stackArray.splice(3,1);
                                msg.stack = stackArray.join('\n\tat ');
                                msg = this._getCallerDetails(msg);
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
                }}

            })
        } catch (err) {
            _logger.error(err.fileName + ", line " + err.lineNumber + ": " + err.message);
        }
    }    

})(this);