import javafx.animation.Animation.Status;
import javafx.animation.KeyFrame;
import javafx.animation.KeyValue;
import javafx.animation.SequentialTransition;
import javafx.animation.Timeline;
import javafx.event.ActionEvent;
import javafx.event.EventHandler;
import javafx.scene.image.Image;
import javafx.scene.image.ImageView;
import javafx.util.Duration;
import main.java.surelyhuman.jdrone.Constants; 

public class Drone extends Item implements DroneAnimationInterface {	
	
	private ImageView image = new ImageView(new Image(getClass().getResourceAsStream("drone.png")));
	private boolean isLaunched;
	private SequentialTransition manualSequence = new SequentialTransition();
	private SequentialTransition autoSequence = new SequentialTransition();
	private double speed = 200.0;
	
	public Drone() {
		super("Drone");
		init();
	}
	
	public Drone(double price, double marketPrice, int xPos, int yPos, int length, int width, int height) {
		super("Drone", price, marketPrice, xPos, yPos, length, width, height);
		init();
	}
	
	private void init() {
		image.setFitHeight(this.length);
		image.setFitWidth(this.width);
		image.setX(this.x);
		image.setY(this.y);
		
		autoSequence = new SequentialTransition();
		
		int passes = 4;
		int tempX = this.getX();
		int tempY = this.getY();
		int passWidth = (Constants.FARMWIDTH - 40) / (passes - 1);
		for (int i = 0; i < passes; i++) {
			autoSequence.getChildren().addAll(calculateGoTo(passWidth * i + 20, 20, tempX, tempY, 0));
			tempX = passWidth * i + 20;
			tempY = 20;
			autoSequence.getChildren().addAll(calculateGoTo(passWidth * i + 20, Constants.FARMHEIGHT - 20, tempX, tempY, -135));
			tempX = passWidth * i + 20;
			tempY = Constants.FARMHEIGHT - 20;
		}
		
		autoSequence.setCycleCount(1);
		autoSequence.setOnFinished(e -> {
			goHome();
		});
		manualSequence.setOnFinished(e -> {
			this.isLaunched = false;
		});
	}
	
	@Override
	public void setLength(int length) {
		super.setLength(length);
		image.setFitHeight(length);
	}
	
	@Override
	public void setWidth(int width) {
		super.setWidth(width);
		image.setFitWidth(width);
	}
	
	public ImageView getImage() {
		return this.image;
	}
	
	public boolean isLaunched() {
		return this.isLaunched;
	}
	
	public boolean isActivated() {
		return true;
	}
	
	public Duration calcDuration(double distance) {
		return Duration.seconds(distance / speed);
	}
	
	private SequentialTransition calculateGoTo(int x, int y, int oldX, int oldY, int oldRotation) {
		int newX = x - (this.getWidth() / 2);
		int newY = y - (this.getLength() / 2);
		int xDistance = newX - oldX; 
		int yDistance = newY - oldY;
		int distance = (int) Math.round(Math.sqrt(Math.pow(yDistance, 2) + Math.pow(xDistance, 2)));
		int rotation = (int) Math.round((Math.toDegrees(Math.atan2(yDistance, xDistance)) % 360)) - 90;
		KeyValue xMove = new KeyValue(image.xProperty(), newX);
		KeyValue yMove = new KeyValue(image.yProperty(), newY);
		KeyValue rotate = new KeyValue(image.rotateProperty(), rotation);
		Timeline rotateTL = new Timeline(new KeyFrame(calcDuration(Math.abs(rotation - oldRotation)), rotate));
		Timeline moveTL = new Timeline(new KeyFrame(calcDuration(distance), xMove, yMove));
		return new SequentialTransition(rotateTL, moveTL);
	}
	
	public void goTo(int x, int y, int z) {
		System.out.println("Currently at: (" + this.getX() + ", " + this.getY() + "), headed to (" + x + ", " + y + ")");
		autoSequence.stop();
		manualSequence.stop();
		manualSequence.getChildren().clear();
		manualSequence.getChildren().addAll(calculateGoTo(x, y, (int) image.getX(), (int) image.getY(), (int) image.getRotate()));
		launch();
		manualSequence.play();
	}
	
	public void scanFarm() {
		launch();
		this.autoSequence.play();
	}
	
	public void visitItem(ItemComponent item) {
		launch();
		goTo(item.getCenterX(), item.getCenterY(), 0);
		EventHandler<ActionEvent> oldEventHandler = manualSequence.getOnFinished();
		manualSequence.setOnFinished(e -> {
			land();
			oldEventHandler.handle(e);
			manualSequence.setOnFinished(oldEventHandler);
		});
	}
	
	public void goHome() {
		goTo(parent.getCenterX(), parent.getCenterY(), 0);
	}
	
	public void launch() {
		this.isLaunched = true;
	}
	
	public void land() {
		goHome();
	}

	public void activate() {
	}
}
