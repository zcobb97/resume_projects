
	
import java.io.IOException;

import javafx.application.Application;
import javafx.fxml.FXMLLoader;
import javafx.stage.Stage;
import main.java.surelyhuman.jdrone.control.physical.tello.demos.TelloFlightDemo;
import javafx.scene.Scene;
import javafx.scene.layout.AnchorPane;

public class Main extends Application {

	private Stage primaryStage;
	private AnchorPane dashboard;
	private ItemContainer rootIC = new ItemContainer("Root");
	public AnchorPane visualize;

	@Override
	public void start(Stage primaryStage) {
		this.primaryStage = primaryStage;
		this.primaryStage.setTitle("Farm Application");
		
		ItemContainer barn = new ItemContainer("Barn", 6000.0, 85, 350, 175, 300, 50);
		ItemContainer livestockArea = new ItemContainer("Livestock Area", 3000.0, 175, 350, 75, 125, 50);
		livestockArea.addItem(new Item("Cow", 200.0, 300.0, 185, 385, 30, 60, 20));
		barn.addItem(livestockArea);
		ItemContainer milkStorage = new ItemContainer("Milk Storage", 400.0, 85, 450, 75, 125, 50);
		barn.addItem(milkStorage);
		this.rootIC.addItem(barn);
		
		ItemContainer storageBuilding = new ItemContainer("Storage Building", 3000.0, 225, 35, 200, 150, 60);
		storageBuilding.addItem(new Item("Tractor", 2000.0, 1000.0, 250, 55, 65, 30, 40));
		storageBuilding.addItem(new Item("Tiller", 500.0, 200.0, 300, 55, 45, 20, 30));
		this.rootIC.addItem(storageBuilding);
		
		ItemContainer commandCenter = new ItemContainer("Command Center", 1000.0, 35, 35, 100, 150, 10);
		commandCenter.addItem(new Drone(500.0, 400.0, commandCenter.getCenterX() - 25, commandCenter.getCenterY() - 25, 50, 50, 10));
		this.rootIC.addItem(commandCenter);
		
		this.rootIC.addItem(new Item("Soy Crop", 100.0, 500.0, 550, 185, 350, 205, 10));
				
		showDashboard();
	}
	
	public void showDashboard() {
		try {
			FXMLLoader loader = new FXMLLoader();
			Dashboard dashboardController = Dashboard.getInstance();
			dashboardController.setRootIC(this.rootIC);
			loader.setLocation(Main.class.getResource("Dashboard.fxml"));
			loader.setController(dashboardController);
			dashboard = (AnchorPane) loader.load();
			
			Scene scene = new Scene(dashboard);
			primaryStage.setScene(scene);
			primaryStage.setResizable(false);
			primaryStage.show();
		} catch (IOException e) {
			e.printStackTrace();
		}
	}
	
	public Stage getPrimaryStage() {
		return primaryStage;
	}
	
	public static void main(String[] args) {
		launch(args);
	}
}
