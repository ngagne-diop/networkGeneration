/* *********************************************************************** *
 * project: org.matsim.*
 * *********************************************************************** *
 *                                                                         *
 * copyright       : (C) 2016 by the members listed in the COPYING,        *
 *                   LICENSE and WARRANTY file.                            *
 * email           : info at matsim dot org                                *
 *                                                                         *
 * *********************************************************************** *
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *   See also COPYING, LICENSE and WARRANTY file                           *
 *                                                                         *
 * *********************************************************************** */

package org.matsim.pt2matsim.workbench;

import org.matsim.core.config.Config;
import org.matsim.core.config.ConfigUtils;
import org.matsim.core.config.ConfigWriter;
import org.matsim.core.utils.collections.CollectionUtils;
import org.matsim.pt2matsim.config.OsmConverterConfigGroup;
import org.matsim.pt2matsim.config.PublicTransitMappingConfigGroup;
import org.matsim.pt2matsim.run.*;

import java.io.File;
import java.io.IOException;

/**
 * Usage test of PT2MATSim to document how the package can be used. The example region
 * is Addison County, USA (except for HAFAS).
 *
 * @author polettif
 *
 * @author adapted by ndiop
 */
public final class PT2MATSimNPDC {

	private static final String example = "npdc/";
	private static final String test = "npdc/";
	private static final String output = "npdc/output/";
	private static final String outputUnmapped = output + "unmapped/";
	private static final String addisonCountyEPSG = "EPSG:2154";

	public static void main(String[] args) {
		prepare();
		// A1.1. Convert a gtfs schedule to an unmapped transit schedule
		gtfsToSchedule();
		// A1.2. OR a hafas schedule to an unmapped transit schedule
		// hafasToSchedule();
		// A1.3. OR an osm file to an unmapped transit schedule
		// Note: osm file cannot be uploaded to github due to its size, see openstreetmap.org or similar for downloads
		// osmToSchedule();
		// A2. Convert an osm map to a network
		osmToNetwork();
		// A3. Map the schedule onto the network
		mapScheduleToNetwork();
		// A4. Do a plausibility check
		checkPlausibility();
	}

	public static void prepare() {
		// Create output folder if not existing:
		new File(output + "plausibilityResults/").mkdirs();
		new File(output + "unmapped/").mkdirs();
	}


	/**
	 * 	1. A GTFS or HAFAS Schedule or a OSM map with information on public transport
	 * 	has to be converted to an unmapped MATSim Transit Schedule.
	 *
	 * 	Here as a first example, the GTFS-schedule of GrandRiverTransit, Waterloo-Area, Canada, is converted.
	 */
	public static void gtfsToSchedule() {
		String[] gtfsConverterArgs = new String[]{
				// [0] folder where the gtfs files are located
				example + "gtfs-fusion/",
				// [1] which service ids should be used. One of the following:
				//		dayWithMostTrips, date in the format yyyymmdd, , dayWithMostServices, all
				"dayWithMostTrips",
				// [2] the output coordinate system. Use WGS84 for no transformation.
				addisonCountyEPSG,
				// [3] output transit schedule file
				outputUnmapped + "schedule_unmapped.xml.gz",
				// [4] output default vehicles file (optional)
				outputUnmapped + "vehicles_unmapped.xml",
		};
		Gtfs2TransitSchedule.main(gtfsConverterArgs);
	}

	/**
	 * 2. A MATSim network of the area is required. If no such network is already available,
	 * the PT2MATSim package provides the possibility to use OSM-maps as data-input.
	 *
	 */
	public static void osmToNetwork() {
		// Create a default osmToNetwork-Config:
		CreateDefaultOsmConfig.main(new String[]{output + "OsmConverterConfigDefault.xml"});

		// Open the osmToNetwork Config and set the parameters to the required values
		// (usually done manually by opening the config with a simple editor)
		Config osmConverterConfig = ConfigUtils.loadConfig(
				output + "OsmConverterConfigDefault.xml",
				new OsmConverterConfigGroup());
		OsmConverterConfigGroup osmConfig = ConfigUtils.addOrGetModule(osmConverterConfig, OsmConverterConfigGroup.class);
		osmConfig.setOsmFile(example + "osm/npdc.osm");
		osmConfig.setOutputCoordinateSystem(addisonCountyEPSG);
		osmConfig.setOutputNetworkFile(example + "npdc.xml");

		// Save the osmToNetwork config (usually done manually)
		new ConfigWriter(osmConverterConfig).write(output + "OsmConverterConfig.xml");

		// Convert the OSM file to a MATSim network using the config
		Osm2MultimodalNetwork.main(new String[]{output + "OsmConverterConfig.xml"});
	}

	/**
	 * 	3. The core of the PT2MATSim-package is the mapping process of the schedule to the network.
	 *
	 * 	Here as an example, the unmapped schedule of GrandRiverTransit (previously converted from GTFS) is mapped
	 * 	to the converted OSM network of the Waterloo Area, Canada.
	 */
	public static void mapScheduleToNetwork() {
		// Create a mapping config:
		CreateDefaultPTMapperConfig.main(new String[]{output + "MapperConfig.xml"});
		// Open the mapping config and set the parameters to the required values
		// (usually done manually by opening the config with a simple editor)
		Config config = ConfigUtils.loadConfig(
				output + "MapperConfig.xml",
				PublicTransitMappingConfigGroup.createDefaultConfig());
		PublicTransitMappingConfigGroup ptmConfig = ConfigUtils.addOrGetModule(config, PublicTransitMappingConfigGroup.class);

		ptmConfig.setInputNetworkFile(example + "npdc.xml");
		ptmConfig.setOutputNetworkFile(output + "npdc-multimodalnetwork.xml.gz");
		ptmConfig.setOutputScheduleFile(output + "npdc-schedule.xml.gz");
		ptmConfig.setOutputStreetNetworkFile(output + "npdc-streetnetwork.xml");
		ptmConfig.setInputScheduleFile(outputUnmapped + "schedule_unmapped.xml.gz");
		ptmConfig.setScheduleFreespeedModes(CollectionUtils.stringToSet("rail, light_rail"));
		// Save the mapping config
		// (usually done manually)
		new ConfigWriter(config).write(output + "MapperConfigAdjusted.xml");

		// Map the schedule to the network using the config
		PublicTransitMapper.main(new String[]{output + "MapperConfigAdjusted.xml"});
	}

	/**
	 * 	4. The PT2MATSim package provides a plausibility checker to get quick feedback on the mapping process.
	 *
	 * 	Here as an example, the mapped transit schedule and the multimodal network created in step 3 is
	 * 	checked for plausibility.
	 */
	public static void checkPlausibility() {
		CheckMappedSchedulePlausibility.run(
				output + "npdc-schedule.xml.gz",
				output + "npdc-multimodalnetwork.xml.gz",
				addisonCountyEPSG,
				output + "plausibilityResults/"
		);
	}


}
