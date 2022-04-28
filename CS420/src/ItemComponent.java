
public interface ItemComponent {

	public ItemContainer getParent();
	
	public void setParent(ItemContainer parent);
	
	public String getName();

	public void setName(String name);

	public double getPrice();

	public void setPrice(double price);

	public int getX();
	
	public int getCenterX();

	public void setX(int x);

	public int getY();
	
	public int getCenterY();

	public void setY(int y);

	public int getLength();

	public void setLength(int length);

	public int getWidth();

	public void setWidth(int width);

	public int getHeight();

	public void setHeight(int height);
	
	public void accept(ItemVisitor vis);
}