exports = {
    createLogger: function(name) {
        return Java.type("org.slf4j.LoggerFactory").getLogger(name);
    },
    logAtLevel: function(logger, level, message) {
        switch(level.toUpperCase()) {
            case 'DEBUG': 
                logger.debug(message);
                break;
            case 'INFO': 
                logger.info(message);
                break;
            case 'WARN': 
                logger.warn(message);
                break;
            case 'ERROR': 
                logger.error(message);
                break;
            default: 
                logger.error("Failed to log at level " + level);
        }
    }
}