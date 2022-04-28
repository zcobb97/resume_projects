import java.io.IOException;

import main.java.surelyhuman.jdrone.Constants;
import main.java.surelyhuman.jdrone.control.physical.tello.TelloDrone;

public class TelloAdapter implements DroneAnimationInterface {
	
	// vars
	private TelloDrone drone;
	private ItemContainer parent;
	private int x, y, z = 0, rotation = 0;
	private boolean isLaunched = false;
	private boolean isActivated = false;
	
	// constructor
	public TelloAdapter(TelloDrone drone, ItemContainer parent) {
		this.drone = drone;
		this.parent = parent;
		this.x = pxToCm(parent.getCenterX());
		this.y = pxToCm(parent.getCenterY());
	}
	
	// getters and setters
	public boolean isLaunched() {
		return this.isLaunched;
	}
	
	public boolean isActivated() {
		return this.isActivated;
	}
	
	// movement functions
	public void goTo(int x, int y, int z) {
		try {
			// calculate movement 
		    x = pxToCm(x); y = pxToCm(y); z = pxToCm(z);
		    double xDist = x - this.x;
		    double yDist = y - this.y;
		    int distance = (int) Math.sqrt(Math.pow(yDist, 2) + Math.pow(xDist, 2));
		    int rotation = (int) Math.round(Math.toDegrees(Math.atan2(yDist, xDist)) % 360);
		    
		    // move drone
		    moveToZ(z);
		    rotateTo(rotation - 90);
		    drone.flyForward(distance);
		    
		    // set local position vars
		    this.x = x;
		    this.y = y;
		} catch (IOException e) {
			e.printStackTrace();
		}
	}
	
	private void rotateTo(int deg) {
		try {
			// decide which to turn clockwise or counter-clockwise
		    if (deg == this.rotation) {
		    	return;
			} else if (deg > this.rotation) {
				drone.turnCW(deg - this.rotation);
		    } else {
		      	drone.turnCCW(this.rotation - deg);
		    }
		     
		    this.rotation = deg;
		} catch (IOException e) {
			e.printStackTrace();
		}
	}
	
	private void moveToZ(int cm) {
		try {
			// decide whether to move up or down
			if (z == cm) {
				return;
			} else if (cm > z) {
				drone.increaseAltitude(cm - z);
			} else {
				drone.decreaseAltitude(z - cm);
			}
		} catch (IOException e) {
			e.printStackTrace();
		}
	}
	
	public void visitItem(ItemComponent item) {
		try { 
			launch();
			goTo(item.getCenterX(), item.getCenterY(), item.getHeight());
			drone.turnCW(360);
			drone.hoverInPlace(3);
			land();
		} catch (IOException | InterruptedException e) {
			e.printStackTrace();
		}

	}
	
	public void scanFarm() {
		launch();
		int passes = 4;
		int passWidth = (Constants.FARMWIDTH - 40) / (passes - 1);
		for (int i = 0; i < passes; i++) {
			goTo(passWidth * i + 20, 20, 0);
			goTo(passWidth * i + 20, Constants.FARMHEIGHT - 20, 0);
		}
		land();
	}
	
	public void launch() {
		try {
			drone.takeoff();
			drone.increaseAltitude(100);
			this.isLaunched = true;
		} catch (IOException e) {
			e.printStackTrace();
		}
	}
	
	public void land() {
		try {
			this.goHome();
			drone.land();
			this.isLaunched = false;
		} catch (IOException e) {
			e.printStackTrace();
		}
	}
	
	public void activate() {
		try {
			drone.activateSDK();
			this.isActivated = true;
		} catch (IOException e) {
			e.printStackTrace();
		}
	}
	
	public void goHome() {
		goTo(parent.getCenterX(), parent.getCenterY(), parent.getHeight());
		rotateTo(0);
	}
	
	// helper functions
	private static int pxToFt(int px) {
		return px / Constants.PIXELS_TO_ONE_MODEL_FOOT;
	}
	
	private static int pxToCm(int px) {
		return pxToFt(px) * Constants.CENTIMETERS_PER_MODEL_FOOT;
	}

}
