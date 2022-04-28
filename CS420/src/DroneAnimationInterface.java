public interface DroneAnimationInterface {
	public void goTo(int x, int y, int z);
	public void scanFarm();
	public void visitItem(ItemComponent item);
	public void goHome();
	public void launch();
	public void land();
	public void activate();
	public boolean isLaunched();
	public boolean isActivated();
}
