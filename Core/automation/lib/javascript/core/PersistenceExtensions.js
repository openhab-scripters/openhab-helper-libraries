/**
 * Functions to aid in using PersistenceExtensions
 * 
 * Copyright (c) 2019 Contributors to the openHAB Scripters project
 * 
 * @author Helmut Lehmeyer - initial contribution
 */
'use strict';

var PersistenceExtensions	= Java.type("org.eclipse.smarthome.model.persistence.extensions.PersistenceExtensions");

//Simplifies spelling for rules.
(function(context) {
  'use strict';
  
	context.PersistenceExtensions 	= PersistenceExtensions;
	context.pe 						= PersistenceExtensions;
	
	context.persistExt = function(type, it, serviceId) {
		try {
			//var item = context.getItem(it);
			//return (serviceId == undefined) ? context.pe[type+""](item) : context.pe[type+""](item, serviceId);
			return (serviceId == undefined) ? context[type+""](it) : context[type+""](it, serviceId);
		}catch(err) {
			context.logError("persistExt " + type +" "+__LINE__, err);
		}
		return null;
	};
	
	//void persist(Item item, String serviceId)
	//void persist(Item item)
	context.persist = function(it, serviceId) {
		try {
			var item = context.getItem(it);
			(serviceId == undefined) ? context.pe.persist(item) : context.pe.persist(item, serviceId);
		}catch(err) {
			context.logError("persist "+__LINE__, err);
		}
	};
	//
	//HistoricItem historicState(Item item, AbstractInstant timestamp)
	//HistoricItem historicState(Item item, AbstractInstant timestamp, String serviceId)
	context.historicState = function(it, timestamp, serviceId) {
		try {
			var item = context.getItem(it);
			return (serviceId == undefined) ? context.pe.historicState(item, timestamp).state : context.pe.historicState(item, timestamp, serviceId).state;
		}catch(err) {
			context.logError("historicState "+__LINE__, err);
		}
		return null;
	};
	//
	//Boolean changedSince(Item item, AbstractInstant timestamp)
	//Boolean changedSince(Item item, AbstractInstant timestamp, String serviceId)
	context.changedSince = function(it, timestamp, serviceId) {
		try {
			var item = context.getItem(it);
			return (serviceId == undefined) ? context.pe.changedSince(item, timestamp) : context.pe.changedSince(item, timestamp, serviceId);
		}catch(err) {
			context.logError("changedSince "+__LINE__, err);
		}
		return null;
	};
	//
	//Boolean updatedSince(Item item, AbstractInstant timestamp)
	//Boolean updatedSince(Item item, AbstractInstant timestamp, String serviceId)
	context.updatedSince = function(it, timestamp, serviceId) {
		try {
			var item = context.getItem(it);
			return (serviceId == undefined) ? context.pe.updatedSince(item, timestamp) : context.pe.updatedSince(item, timestamp, serviceId);
		}catch(err) {
			context.logError("updatedSince "+__LINE__, err);
		}
		return null;
	};
	//
	//HistoricItem maximumSince(Item item, AbstractInstant timestamp)
	//HistoricItem maximumSince(final Item item, AbstractInstant timestamp, String serviceId)
	context.maximumSince = function(it, timestamp, serviceId) {
		try {
			var item = context.getItem(it);
			return (serviceId == undefined) ? context.pe.maximumSince(item, timestamp).state : context.pe.maximumSince(item, timestamp, serviceId).state;
		}catch(err) {
			context.logError("maximumSince "+__LINE__, err);
		}
		return null;
	};
	//
	//HistoricItem minimumSince(Item item, AbstractInstant timestamp)
	//HistoricItem minimumSince(final Item item, AbstractInstant timestamp, String serviceId)
	context.minimumSince = function(it, timestamp, serviceId) {
		try {
			var item = context.getItem(it);
			return (serviceId == undefined) ? context.pe.minimumSince(item, timestamp).state : context.pe.minimumSince(item, timestamp, serviceId).state;
		}catch(err) {
			context.logError("minimumSince "+__LINE__, err);
		}
		return null;
	};
	//
	//DecimalType averageSince(Item item, AbstractInstant timestamp)
	//DecimalType averageSince(Item item, AbstractInstant timestamp, String serviceId)
	context.averageSince = function(it, timestamp, serviceId) {
		try {
			var item = context.getItem(it);
			return (serviceId == undefined) ? context.pe.averageSince(item, timestamp) : context.pe.averageSince(item, timestamp, serviceId);
		}catch(err) {
			context.logError("averageSince "+__LINE__, err);
		}
		return null;
	};
	//
	//DecimalType sumSince(Item item, AbstractInstant timestamp)
	//DecimalType sumSince(Item item, AbstractInstant timestamp, String serviceId)
	context.sumSince = function(it, timestamp, serviceId) {
		try {
			var item = context.getItem(it);
			return (serviceId == undefined) ? context.pe.sumSince(item, timestamp) : context.pe.sumSince(item, timestamp, serviceId);
		}catch(err) {
			context.logError("sumSince "+__LINE__, err);
		}
		return null;
	};
	//
	//AbstractInstant lastUpdate(Item item)
	//AbstractInstant lastUpdate(Item item, String serviceId)
	context.lastUpdate = function(it, serviceId) {
		try {
			var item = context.getItem(it);
			return (serviceId == undefined) ? context.pe.lastUpdate(item) : context.pe.lastUpdate(item, serviceId);
		}catch(err) {
			context.logError("lastUpdate "+__LINE__, err);
		}
		return null;
	};
	//
	//DecimalType deltaSince(Item item, AbstractInstant timestamp)
	//DecimalType deltaSince(Item item, AbstractInstant timestamp, String serviceId)
	context.deltaSince = function(it, timestamp, serviceId) {
		try {
			var item = context.getItem(it);
			return (serviceId == undefined) ? context.pe.deltaSince(item, timestamp) : context.pe.deltaSince(item, timestamp, serviceId);
		}catch(err) {
			context.logError("deltaSince "+__LINE__, err);
		}
		return null;
	};
	//
	//DecimalType evolutionRate(Item item, AbstractInstant timestamp)
	//DecimalType evolutionRate(Item item, AbstractInstant timestamp, String serviceId)
	context.evolutionRate = function(it, timestamp, serviceId) {
		try {
			var item = context.getItem(it);
			return (serviceId == undefined) ? context.pe.evolutionRate(item, timestamp) : context.pe.evolutionRate(item, timestamp, serviceId);
		}catch(err) {
			context.logError("evolutionRate "+__LINE__, err);
		}
		return null;
	};
	//
	//HistoricItem previousState(Item item)
	//HistoricItem previousState(Item item, boolean skipEqual)
	//HistoricItem previousState(Item item, boolean skipEqual, String serviceId)
	context.previousState = function(it, skipEqual, serviceId) {
		try {
			skipEqual = skipEqual == undefined ? false : skipEqual;
			var item = context.getItem(it);
			return (serviceId == undefined) ? context.pe.previousState(item, skipEqual).state : context.pe.previousState(item, skipEqual, serviceId).state;
		}catch(err) {
			context.logError("previousState "+__LINE__, err);
		}
		return null;
	};
  
})(this);
