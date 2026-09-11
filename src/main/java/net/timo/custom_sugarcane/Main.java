package net.timo.custom_sugarcane;

import net.fabricmc.api.ModInitializer;
import net.timo.custom_sugarcane.item.ModItems;
import org.slf4j.LoggerFactory;
import org.slf4j.Logger;

public class Main implements ModInitializer {
	public static final String MOD_ID = "custom_sugarcane";
	public static final Logger LOGGER = LoggerFactory.getLogger(MOD_ID);
	@Override
	public void onInitialize() {
		ModItems.registerModItems();
	}
}