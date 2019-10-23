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

    context.Logger = function Logger (_name, _notificationLevel, _config) {

        var LOGGER_PREFIX = "org.eclipse.smarthome.model.script.jsr223.javascript";

        var PATH_SEPARATOR = Java.type("java.lang.System").getenv("OPENHAB_CONF").split(Java.type("java.lang.System").getenv("OPENHAB_HOME")).pop()[0];
        var AUTOMATION_PATH = Java.type("java.lang.System").getenv("OPENHAB_CONF")
        if (PATH_SEPARATOR === "\\") AUTOMATION_PATH = AUTOMATION_PATH.replace(/\\/g,'/');
        AUTOMATION_PATH = AUTOMATION_PATH + "/automation/";

        if (_name === undefined) {
            _name = Error().stack.split('\n')[2].split('/').slice(-2).join('.').split(':')[0];
            _name = _name.slice(-3) == ".js" ? _name.slice(0,-3) : null;
        }
        var _logger  = Java.type("org.slf4j.LoggerFactory").getLogger(_name === null ? LOGGER_PREFIX : LOGGER_PREFIX + "." + _name.toString().toLowerCase());

        try {
            // Set default config for config params not provided.
            if (_config === undefined) _config = {};
            if (_config.ERROR === undefined) _config.ERROR = {};
            if (_config.WARN  === undefined) _config.WARN  = {};
            if (_config.INFO  === undefined) _config.INFO  = {};
            if (_config.DEBUG === undefined) _config.DEBUG = {};
            if (_config.ERROR.prefix === undefined) _config.ERROR.prefix = "short";
            if (_config.WARN.prefix  === undefined) _config.WARN.prefix  = "none";
            if (_config.INFO.prefix  === undefined) _config.INFO.prefix  = "none";
            if (_config.DEBUG.prefix === undefined) _config.DEBUG.prefix = "short";

            var _MessageFormatter = Java.type("org.slf4j.helpers.MessageFormatter");

            var _getLogMessage = function _getLogMessage (msg, prefix, levelString) {
                if (msg instanceof Error) {
                    msg.caller = msg.stack.split('\n\tat ')[1].split(' (')[0]
                } else {
                    msg = Error(msg);
                    msg = _getCallerDetails(msg);
                }
                msg = _legacyLoggerCorrection(msg);

                if (prefix === undefined) prefix = "log";

                if (prefix == "none") {
                    return msg.message;
                }

                var level = "";
                var nameText = "";
                if (prefix != "log") {
                    level = "[" + levelString + "] ";
                    nameText = _name === null ? "" : _name;
                }

                if (prefix == "level") {
                    return (level + msg.message);
                }

                var callerText;
                if (msg.caller.substr(0,1) == "<") {
                    callerText = ", in " + msg.caller;
                } else {
                    callerText = ", function " + msg.caller;
                }

                var message = msg.message == "" ? "" : msg.message + " ";

                if (prefix == "short") {
                    return (level + message + "\t\t[" + (nameText != "" ? nameText + ", " : "") + msg.fileName.split('/').pop() + ":" + msg.lineNumber + callerText + "]");
                }
                return (level + message + "\t\t[" + (nameText != "" ? nameText + ": " : "") + "at source " + msg.fileName.split(AUTOMATION_PATH).pop() + ", line " + msg.lineNumber + callerText + "]");
            }

            var _getCallerDetails = function _getCallerDetails (msg) {
                var matches = msg.stack.split('\n\tat ')[3].match(/(.+?) \((.+):(\d+?)\)/);
                msg.caller = matches[1];
                msg.fileName = matches[2]
                msg.lineNumber = matches[3]
                return msg;
            }

            var _sendNotification = function _sendNotification (message, icon, levelString, log) {
                if (_config[levelString].recipients !== undefined) {
                    _config[levelString].recipients.forEach(function(mail){
                        NotificationAction.sendNotification(mail, message, icon, levelString);
                    })
                    if (_config[levelString].recipients.length > 0) {
                        log.trace(Error("Notification sent to " + _config[levelString].recipients.join(", ") + ". Message: \"" + message + "\""));
                    }
                } else {
                    NotificationAction.sendBroadcastNotification(message, icon, levelString);
                    log.trace(Error("Broadcast notification sent. Message: \"" + message + "\""));
                }
            }

            var _legacyLoggerCorrection = function _legacyLoggerCorrection (msg) {
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
                            msg = _getCallerDetails(msg);
                        }
                }
                return msg;
            }

            return Object.create(Object.prototype, {
                notificationLevel: { value: (_notificationLevel === undefined || _notificationLevel === null) ? context.NOTIFY_OFF : _notificationLevel },
                config: { value: _config },
                name: { value: _name },

                error: { value: function error (msg) {
                    try {
                        if (_logger.isErrorEnabled()) {
                            _logger.error(_getLogMessage(msg), [].slice.call(arguments).slice(1));
                        }
                        if (this.notificationLevel >= context.NOTIFY_ERROR) {
                            _sendNotification(_MessageFormatter.arrayFormat(_getLogMessage(msg, this.config.ERROR.prefix, "ERROR"), [].slice.call(arguments).slice(1)).getMessage(), "fire", "ERROR", this);
                        }
                    } catch (err) {
                        _logger.error(_getLogMessage(err));
                    }
                }},

                warn: { value: function warn (msg) {
                    try {
                        if (_logger.isWarnEnabled()) {
                            _logger.warn(_getLogMessage(msg), [].slice.call(arguments).slice(1));
                        }
                        if (this.notificationLevel >= context.NOTIFY_WARN) {
                            _sendNotification(_MessageFormatter.arrayFormat(_getLogMessage(msg, this.config.WARN.prefix, "WARN"), [].slice.call(arguments).slice(1)).getMessage(), "error", "WARN", this);
                        }
                    } catch (err) {
                        _logger.error(_getLogMessage(err));
                    }
                }},

                info: { value: function info (msg) {
                    try {
                        if (_logger.isInfoEnabled()) {
                            _logger.info(_getLogMessage(msg), [].slice.call(arguments).slice(1));
                        }
                        if (this.notificationLevel >= context.NOTIFY_INFO) {
                            _sendNotification(_MessageFormatter.arrayFormat(_getLogMessage(msg, this.config.INFO.prefix, "INFO"), [].slice.call(arguments).slice(1)).getMessage(), "lightbulb", "INFO", this);
                        }
                    } catch (err) {
                        _logger.error(_getLogMessage(err));
                    }
                }},

                debug: { value: function debug (msg) {
                    try {
                        if (_logger.isDebugEnabled()) {
                            _logger.debug(_getLogMessage(msg), [].slice.call(arguments).slice(1));
                        }
                        if (this.notificationLevel >= context.NOTIFY_DEBUG) {
                            _sendNotification(_MessageFormatter.arrayFormat(_getLogMessage(msg, this.config.DEBUG.prefix, "DEBUG"), [].slice.call(arguments).slice(1)).getMessage(), "text", "DEBUG", this);
                        }
                    } catch (err) {
                        _logger.error(_getLogMessage(err));
                    }
                }},

                trace: { value: function trace (msg) {
                    try {
                        if (_logger.isTraceEnabled()) {
                            _logger.trace(_getLogMessage(msg), [].slice.call(arguments).slice(1));
                        }
                    } catch (err) {
                        _logger.error(_getLogMessage(err));
                    }
                }}

            })
        } catch (err) {
            _logger.error(err.message + " [source " + err.fileName + ", line " + err.lineNumber + "]");
        }
    }

})(this);
