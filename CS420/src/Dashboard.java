



import java.io.FileNotFoundException;
import java.net.SocketException;
import java.net.UnknownHostException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Hashtable;
import java.util.Optional;

import javafx.beans.value.ChangeListener;
import javafx.beans.value.ObservableValue;
import javafx.fxml.FXML;
import javafx.geometry.Insets;
import javafx.scene.control.Alert;
import javafx.scene.control.Alert.AlertType;
import javafx.scene.image.Image;
import javafx.scene.image.ImageView;
import javafx.scene.layout.AnchorPane;
import javafx.scene.layout.GridPane;
import javafx.scene.layout.HBox;
import javafx.scene.paint.Color;
import javafx.scene.shape.Rectangle;
import javafx.scene.text.Text;
import javafx.stage.Window;
import main.java.surelyhuman.jdrone.control.physical.tello.TelloDrone;
import javafx.scene.control.ButtonType;
import javafx.scene.control.ContextMenu;
import javafx.scene.control.Dialog;
import javafx.scene.control.Label;
import javafx.scene.control.MenuItem;
import javafx.scene.control.RadioButton;
import javafx.scene.control.TextField;
import javafx.scene.control.TextInputDialog;
import javafx.scene.control.TreeItem;
import javafx.scene.control.TreeView;

public class Dashboard {
	// vars
	@FXML
	private TreeView<String> itemsTree;
	
	@FXML
	private RadioButton droneManualButton;
	
	@FXML
	private RadioButton droneAutoButton;
	
	@FXML
	private AnchorPane map;
	
	@FXML
	private Label priceLabel;
	
	@FXML
	private Label marketValueLabel;
	
	private ItemContainer rootIC;
	private static Dashboard dashboardInstance = new Dashboard();
	private Drone simulatedDrone;
	private TelloAdapter physicalDrone;
	private Hashtable<TreeItem<String>, ItemComponent> treeMap = new Hashtable<TreeItem<String>, ItemComponent>();
	private ContextMenu itemMenu = new ContextMenu();
	private ContextMenu itemContainerMenu = new ContextMenu();
	private TreeItem<String> selectedItem;
	
	// constructor
	private Dashboard() {}
	
	// getInstance func for singleton
	public static Dashboard getInstance() { 
		return dashboardInstance; 
	}
	
	public void setRootIC(ItemContainer rootIC) {
		this.rootIC = rootIC;
	}
	
	@FXML
	private void launchSimulator() {
		handleDroneLaunch(simulatedDrone);
	}
	
	@FXML
	private void launchPhysical() {
		if (!physicalDrone.isActivated()) physicalDrone.activate();
		handleDroneLaunch(physicalDrone);
	}
	
	private void handleDroneLaunch(DroneAnimationInterface drone) {
		if (!drone.isLaunched()) {
			if (droneAutoButton.isSelected()) {
				drone.scanFarm();
			} else if (droneManualButton.isSelected() && selectedItem != null) {
				ItemComponent item = treeMap.get(selectedItem);
				if (item.getName() != "Root" && !(item instanceof Drone)) {
					drone.visitItem(item);
				}
			}
		} else {
			Alert a = new Alert(AlertType.ERROR);
			a.setContentText("Drone is already launched, cannot launch again.");
			a.show();
		}
	}
	
	TreeItem<String> itemToTreeItem(ItemComponent rootItem, TreeItem<String> rootTreeItem) {
		if (rootItem.getClass() == ItemContainer.class) {
			// create tree item for container
			TreeItem<String> treeContainer = new TreeItem<String>("");
			ItemContainer itemContainer = (ItemContainer) rootItem;
			
			// add TreeItem to dict mapped to ItemContainer
			this.treeMap.put(treeContainer, itemContainer);
			
			treeContainer.setExpanded(true);
			
			AnchorPane treeItemLabel = new AnchorPane(new HBox(new ImageView(new Image(getClass().getResourceAsStream("folder.png"))),  new Label(itemContainer.getName())));

			// attach context menu to TreeItem
			treeItemLabel.setOnContextMenuRequested(e -> {
				boolean isRoot = itemContainer.getName() == "Root";
				boolean isCommandCenter = itemContainer.getName() == "Command Center";
				if (isRoot || isCommandCenter) {
					// disable all options except add for root container and delete for command center
					itemContainerMenu.getItems().forEach(mi -> {
						boolean disableForRoot = !(mi.getText() == "Add Item" || mi.getText() == "Add Item Container");
						boolean disableForCommandCenter = mi.getText() == "Delete";
						if ((isRoot && disableForRoot) || (isCommandCenter && disableForCommandCenter)) {
							mi.setDisable(true);
						}
					});
					
					// re-enable options once menu closes
					itemContainerMenu.setOnHiding(me -> {
						itemContainerMenu.getItems().forEach(mi -> {
							mi.setDisable(false);
						});
						itemContainerMenu.setOnHiding(null);
					});
				}
				
			    // show context menu
			    itemContainerMenu.show(treeContainer.getGraphic(), e.getScreenX(), e.getScreenY());  
			});
			
			treeContainer.setGraphic(treeItemLabel);

	        // run again for each container item and add  
			if (!itemContainer.getItems().isEmpty()) {
				for (int i = 0; i < (itemContainer.getItems().size()); i++) {
					treeContainer.getChildren().add(itemToTreeItem(((ItemContainer) rootItem).getItems().get(i), treeContainer));
				}
			}
			
			return treeContainer;
		} else {			
			// create TreeItem for Item
			TreeItem<String> treeItem = new TreeItem<String>("");
			Item item = (Item) rootItem;
			
			// add TreeItem to dict mapped to Item
			this.treeMap.put(treeItem, item);
			
			
			AnchorPane treeItemLabel = new AnchorPane(new HBox(new ImageView(new Image(getClass().getResourceAsStream("file.png"))),  new Label(item.getName())));
			
			// attach context menu to TreeItem
			treeItemLabel.setOnContextMenuRequested(e -> {
				boolean isDrone = item.getName() == "Drone";
				if (isDrone) {
					itemMenu.getItems().forEach(mi -> {
						boolean disableForDrone = mi.getText() == "Change Location" || mi.getText() == "Delete";
						if (disableForDrone) {
							mi.setDisable(true);
						}
					});
					
					// re-enable options once menu closes
					itemMenu.setOnHiding(me -> {
						itemMenu.getItems().forEach(mi -> {
							mi.setDisable(false);
						});
						itemMenu.setOnHiding(null);
					});
				}
			    // show context menu
			    itemMenu.show(treeItem.getGraphic(), e.getScreenX(), e.getScreenY());  
			});
			
			treeItem.setGraphic(treeItemLabel);
			return treeItem;
		}
	}
	
	// map drawing funcs
	public void drawAllItems() {
		this.map.getChildren().clear();
		ItemContainer.toArrayList(rootIC).forEach(item -> {
			if (!(item.getClass() == Drone.class)) {
				drawItem(item, map);
			} else {
				if (simulatedDrone == null) { simulatedDrone = (Drone) item; }
				if (physicalDrone == null) {
					try {
						physicalDrone = new TelloAdapter(new TelloDrone(), simulatedDrone.getParent());
					} catch (SocketException | UnknownHostException | FileNotFoundException e) {
						e.printStackTrace();
					}
				}
				map.getChildren().add(simulatedDrone.getImage());
			}
		});
	}
	
	public void drawItem(ItemComponent item, AnchorPane root) {
		Rectangle rectangle = new Rectangle();
		Text text = new Text((double) item.getX(), (double) item.getY(), item.getName());
		rectangle.setWidth(item.getWidth()); 
		rectangle.setHeight(item.getLength());
		rectangle.setFill(Color.TRANSPARENT);
		rectangle.setStroke(Color.BLACK);
		AnchorPane.setTopAnchor(rectangle, (double) item.getY());
		AnchorPane.setLeftAnchor(rectangle, (double) item.getX());
		AnchorPane.setRightAnchor(rectangle, 10.0);
		AnchorPane.setBottomAnchor(rectangle, 10.0);
		
		root.getChildren().addAll(rectangle, text);   
	}

	// ui setup
	@FXML
	private void initialize() {
		TreeItem<String> rootTI = itemToTreeItem(rootIC, new TreeItem<String>("Root"));
		itemsTree.setRoot(rootTI);
		itemsTree.getSelectionModel().selectedItemProperty().addListener(new ChangeListener<Object>() {
			@SuppressWarnings({ "unchecked", "rawtypes" })
			@Override
			public void changed(ObservableValue observable, Object oldValue, Object newValue) {
				selectedItem = (TreeItem<String>) newValue;
				if (selectedItem != null) {
					ItemComponent item = treeMap.get(selectedItem);
					PriceVisitor pv = new PriceVisitor();
					MarketValueVisitor mv = new MarketValueVisitor();
					item.accept(pv);
					item.accept(mv);
					priceLabel.setText("$" + String.format("%.2f", pv.getPrice()));
					marketValueLabel.setText("$" + String.format("%.2f", mv.getMarketValue()));
				}
			}
		});
		drawAllItems();
		
		// create context menu options
		MenuItem addItem = new MenuItem("Add Item");
		MenuItem addItemContainer = new MenuItem("Add Item Container");
		MenuItem deleteOption = new MenuItem("Delete");
		MenuItem changeNameOption = new MenuItem("Change Name");
		MenuItem changePriceOption = new MenuItem("Change Price");
		MenuItem changeMarketValueOption = new MenuItem("Change Market Value");
		MenuItem changeLocationOption = new MenuItem("Change Location");
		MenuItem changeDimensionsOption = new MenuItem("Change Dimensions");
		
		addItem.setOnAction(e -> {
    		ItemContainer itemContainer = (ItemContainer) treeMap.get(selectedItem);
			Dialog<ButtonType> dialog = new Dialog<ButtonType>();
	    	Window window = dialog.getDialogPane().getScene().getWindow();
	    	window.setOnCloseRequest(we -> {
	    		window.hide();
	    	});

	    	if (e.getSource() == addItem) {
		    	dialog.setTitle("Add Item");
	    	} else {
	    		dialog.setTitle("Add Item Container");
	    	}

	    	GridPane grid = new GridPane();
	    	Label nameLabel = new Label("Name");
	    	nameLabel.setPadding(new Insets(0, 20, 0, 0));
	    	TextField nameTextField = new TextField((e.getSource() == addItem) ? "New Item" : "New Item Container");
	    	Label priceLabel = new Label("Price");
	    	priceLabel.setPadding(new Insets(0, 20, 0, 0));
	    	TextField priceTextField = new TextField("0.0");
	    	Label xLabel = new Label("X Position");
	    	xLabel.setPadding(new Insets(0, 20, 0, 0));
	    	TextField xTextField = new TextField("0");
	    	Label yLabel = new Label("Y Position");
	    	yLabel.setPadding(new Insets(0, 20, 0, 0));
	    	TextField yTextField = new TextField("0");
	    	Label lengthLabel = new Label("Length");
	    	lengthLabel.setPadding(new Insets(0, 20, 0, 0));
	    	TextField lengthTextField = new TextField("100");
	    	Label widthLabel = new Label("Width");
	    	widthLabel.setPadding(new Insets(0, 20, 0, 0));
	    	TextField widthTextField = new TextField("100");
	    	Label heightLabel = new Label("Height");
	    	heightLabel.setPadding(new Insets(0, 20, 0, 0));
	    	TextField heightTextField = new TextField("100");
	    	grid.addRow(0, nameLabel, nameTextField);
	    	grid.addRow(1, priceLabel, priceTextField);
	    	grid.addRow(2, xLabel, xTextField);
	    	grid.addRow(3, yLabel, yTextField);
	    	grid.addRow(4, lengthLabel, lengthTextField);
	    	grid.addRow(5, widthLabel, widthTextField);
	    	grid.addRow(6, heightLabel, heightTextField);
	    	grid.setVgap(10);
	    	dialog.getDialogPane().setContent(grid);
	    	dialog.getDialogPane().getButtonTypes().addAll(ButtonType.OK, ButtonType.CANCEL);
	    	dialog.setOnCloseRequest(ce -> {
	    		if (dialog.getResult() == ButtonType.OK) {
		    		try {
		    			String name = nameTextField.getText();
		    			double price = Double.parseDouble(priceTextField.getText());
		    			int x = Integer.parseInt(xTextField.getText());
		    			int y = Integer.parseInt(yTextField.getText());
		    			int length = Integer.parseInt(lengthTextField.getText());
		    			int width = Integer.parseInt(widthTextField.getText());
		    			int height = Integer.parseInt(heightTextField.getText());
		    			
		    			ItemComponent newItem;
		    	    	if (e.getSource() == addItem) {
		    	    		newItem = new Item(name);
		    	    	} else {
		    	    		newItem = new ItemContainer(name);
		    	    	}
		    	    	newItem.setPrice(price);
						newItem.setX(x);
		    			newItem.setY(y);
		    			newItem.setLength(length);
		    			newItem.setWidth(width);
		    			newItem.setHeight(height);
		    			
		    			itemContainer.addItem(newItem);
		    			TreeItem<String> newTreeItem = itemToTreeItem(newItem, new TreeItem<String>(name));
		    			selectedItem.getChildren().add(newTreeItem);
		    			itemsTree.getSelectionModel().select(newTreeItem);
		    			drawAllItems();
		    		} catch (NumberFormatException err) {
	        			Alert alert = new Alert(AlertType.ERROR);
	        			alert.setTitle("Input error");
	        			alert.setHeaderText(null);
	        			alert.setContentText("One or more of the values is invalid.");
	        			alert.showAndWait();
	        			e.consume();
		    		}
	    		}
	    	});
	    	dialog.show();
		});
		
		addItemContainer.setOnAction(addItem.getOnAction());
		
		deleteOption.setOnAction(e -> {
    		ItemComponent item = treeMap.get(selectedItem);
	    	Alert alert = new Alert(AlertType.CONFIRMATION);
	    	alert.setTitle("Confirm Deletion");
	    	alert.setHeaderText(null);
	    	alert.setContentText("Are you sure you want to delete " + item.getName() + "?");

	    	Optional<ButtonType> result = alert.showAndWait();
	    	if (result.get() == ButtonType.OK){
	    		treeMap.get(selectedItem).getParent().removeItem(item);
		    	selectedItem.getParent().getChildren().remove(selectedItem);
		    	drawAllItems();
	    	}
		});
				
		changeNameOption.setOnAction(e -> {
    		ItemComponent item = treeMap.get(selectedItem);
	        // create a text input dialog
	        TextInputDialog dialog = new TextInputDialog(treeMap.get(selectedItem).getName());
	  
	        dialog.setHeaderText("Enter new name");
	        dialog.setTitle("Update Item");
	        dialog.setGraphic(null);
	        dialog.setOnCloseRequest(ce -> {
        		String result = ((TextInputDialog) e.getSource()).getResult();
        		if (result != null) {
	        		if (result.length() >= 1) {
		        		item.setName(result);
				    	((Label) selectedItem.getGraphic()).setText(result);
				    	drawAllItems();
	        		} else {
	        			Alert alert = new Alert(AlertType.ERROR);
	        			alert.setTitle("Input error");
	        			alert.setHeaderText(null);
	        			alert.setContentText("Name must have at least 1 character.");
	        			alert.showAndWait();
	        			e.consume();
	        		}
        		}
	        });
	        dialog.show();
		});

		changePriceOption.setOnAction(e -> {
	        // create a text input dialog
    		TreeItem<String> treeItem = selectedItem;
    		ItemComponent item = treeMap.get(treeItem);
	        TextInputDialog dialog = new TextInputDialog(Double.toString(item.getPrice()));
	  
	        dialog.setHeaderText("Enter new price");
	        dialog.setTitle("Update Item");
	        dialog.setGraphic(null);
	        dialog.setOnCloseRequest(ce -> {
        		String result = ((TextInputDialog) e.getSource()).getResult();
        		if (result != null) {
	        		try {
	        			item.setPrice(Double.parseDouble(result));
	        			itemsTree.getSelectionModel().clearSelection();
		    			itemsTree.getSelectionModel().select(treeItem);
	        		} catch (NumberFormatException err) {
	        			Alert alert = new Alert(AlertType.ERROR);
	        			alert.setTitle("Input error");
	        			alert.setHeaderText(null);
	        			alert.setContentText("Number is invalid.");
	        			alert.showAndWait();
	        			e.consume();
	        		}
        		}
	        });
	        dialog.show();
		});
		
		changeMarketValueOption.setOnAction(e -> {
	        // create a text input dialog
			TreeItem<String> treeItem = selectedItem;
    		Item item = (Item) treeMap.get(treeItem);
	        TextInputDialog dialog = new TextInputDialog(Double.toString(item.getMarketValue()));
	  
	        dialog.setHeaderText("Enter new price");
	        dialog.setTitle("Update Item");
	        dialog.setGraphic(null);
	        dialog.setOnCloseRequest(ce -> {
        		String result = ((TextInputDialog) e.getSource()).getResult();
        		if (result != null) {
	        		try {
	        			item.setMarketValue(Double.parseDouble(result));
	        			itemsTree.getSelectionModel().clearSelection();
	        			itemsTree.getSelectionModel().select(treeItem);
	        		} catch (NumberFormatException err) {
	        			Alert alert = new Alert(AlertType.ERROR);
	        			alert.setTitle("Input error");
	        			alert.setHeaderText(null);
	        			alert.setContentText("Number is invalid.");
	        			alert.showAndWait();
	        			e.consume();
	        		}
        		}
	        });
	        dialog.show();
		});
		
		changeLocationOption.setOnAction(e -> {
    		ItemComponent item = treeMap.get(selectedItem);
			Dialog<ButtonType> dialog = new Dialog<ButtonType>();
	    	Window window = dialog.getDialogPane().getScene().getWindow();
	    	window.setOnCloseRequest(we -> {
	    		window.hide();
	    	});
	    	dialog.setTitle("Change Location");
	    	
	    	GridPane grid = new GridPane();
	    	Label xLabel = new Label("X Position");
	    	xLabel.setPadding(new Insets(0, 20, 0, 0));
	    	TextField xTextField = new TextField("" + item.getX());
	    	Label yLabel = new Label("Y Position");
	    	yLabel.setPadding(new Insets(0, 20, 0, 0));
	    	TextField yTextField = new TextField("" + item.getY());
	    	grid.addRow(0, xLabel, xTextField);
	    	grid.addRow(1, yLabel, yTextField);
	    	grid.setVgap(10);
	    	dialog.getDialogPane().setContent(grid);
	    	dialog.getDialogPane().getButtonTypes().addAll(ButtonType.OK, ButtonType.CANCEL);
	    	dialog.setOnCloseRequest(ce -> {
	    		if (dialog.getResult() == ButtonType.OK) {
		    		try {
		    			int x = Integer.parseInt(xTextField.getText());
		    			int y = Integer.parseInt(yTextField.getText());
		    			item.setX(x);
		    			item.setY(y);
		    			drawAllItems();
		    		} catch (NumberFormatException err) {
	        			Alert alert = new Alert(AlertType.ERROR);
	        			alert.setTitle("Input error");
	        			alert.setHeaderText(null);
	        			alert.setContentText("One or more of the values is invalid.");
	        			alert.showAndWait();
	        			e.consume();
		    		}
	    		}
	    	});
	    	dialog.show();
		});
		
		changeDimensionsOption.setOnAction(e -> {
    		ItemComponent item = treeMap.get(selectedItem);
			Dialog<ButtonType> dialog = new Dialog<ButtonType>();
	    	Window window = dialog.getDialogPane().getScene().getWindow();
	    	window.setOnCloseRequest(we -> {
	    		window.hide();
	    	});
	    	dialog.setTitle("Change Dimensions");
	    	
	    	GridPane grid = new GridPane();
	    	Label lengthLabel = new Label("Length");
	    	lengthLabel.setPadding(new Insets(0, 20, 0, 0));
	    	TextField lengthTextField = new TextField("" + item.getLength());
	    	Label widthLabel = new Label("Width");
	    	widthLabel.setPadding(new Insets(0, 20, 0, 0));
	    	TextField widthTextField = new TextField("" + item.getWidth());
	    	Label heightLabel = new Label("Height");
	    	heightLabel.setPadding(new Insets(0, 20, 0, 0));
	    	TextField heightTextField = new TextField("" + item.getHeight());
	    	grid.addRow(0, lengthLabel, lengthTextField);
	    	grid.addRow(1, widthLabel, widthTextField);
	    	grid.addRow(2, heightLabel, heightTextField);
	    	grid.setVgap(10);
	    	dialog.getDialogPane().setContent(grid);
	    	dialog.getDialogPane().getButtonTypes().addAll(ButtonType.OK, ButtonType.CANCEL);
	    	dialog.setOnCloseRequest(ce -> {
	    		if (dialog.getResult() == ButtonType.OK) {
		    		try {
		    			int length = Integer.parseInt(lengthTextField.getText());
		    			int width = Integer.parseInt(widthTextField.getText());
		    			int height = Integer.parseInt(heightTextField.getText());
		    			item.setLength(length);
		    			item.setWidth(width);
		    			item.setHeight(height);
		    			drawAllItems();
		    		} catch (NumberFormatException err) {
	        			Alert alert = new Alert(AlertType.ERROR);
	        			alert.setTitle("Input error");
	        			alert.setHeaderText(null);
	        			alert.setContentText("One or more of the values is invalid.");
	        			alert.showAndWait();
	        			e.consume();
		    		}
	    		}
	    	});
	    	dialog.show();
		});
		
		
		// set up context menus
		itemContainerMenu.getItems().addAll(addItem, addItemContainer);

		ArrayList<MenuItem> sharedItems = new ArrayList<MenuItem>();
		Collections.addAll(sharedItems, deleteOption, changeNameOption, changePriceOption, changeLocationOption, changeDimensionsOption);
		
		sharedItems.forEach(menuItem -> {
			itemMenu.getItems().add(menuItem);
			MenuItem menuItemClone = new MenuItem(menuItem.getText());
			menuItemClone.setOnAction(menuItem.getOnAction());
			itemContainerMenu.getItems().add(menuItemClone);
		});
		itemMenu.getItems().add(3, changeMarketValueOption);
		
	}
}
