
public class Item implements ItemComponent {
	// vars
	protected ItemContainer parent;
	private String name;
	private double price;
	private double marketValue;
	protected int x;
	protected int y;
	protected int length;
	protected int width;
	protected int height;
	
	// constructors	
	public Item(String name, double price, double marketValue, int x, int y, int length, int width, int height) {
		super();
		this.name = name;
		this.price = price;
		this.marketValue = marketValue;
		this.x = x;
		this.y = y;
		this.length = length;
		this.width = width;
		this.height = height;
	}
	
	public Item(String name) {
		super();
		this.name = name;
		this.price = 0.0;
		this.x = 0;
		this.y = 0;
		this.length = 0;
		this.width = 0;
		this.height = 0;
	}
	
	// toString
	public String toString() {
		return this.getName();
	}
	
	// getters and setters
	public ItemContainer getParent() {
		return this.parent;
	}
	
	public void setParent(ItemContainer parent) {
		this.parent = parent;
	}
	
	public String getName() {
		return name;
	}
	
	public void setName(String name) {
		this.name = name;
	}
	
	public double getPrice() {
		return price;
	}
	
	public void setPrice(double price) {
		this.price = price;
	}
	
	public double getMarketValue() {
		return marketValue;
	}

	public void setMarketValue(double marketValue) {
		this.marketValue = marketValue;
	}
	
	public int getX() {
		return x;
	}
	
	public int getCenterX() {
		return x + (width / 2);
	}
	
	public void setX(int x) {
		this.x = x;
	}
	
	public int getY() {
		return y;
	}
	
	public int getCenterY() {
		return y + (length / 2);
	}
	
	public void setY(int yPos) {
		this.y = yPos;
	}
	
	public int getLength() {
		return length;
	}
	
	public void setLength(int length) {
		this.length = length;
	}
	
	public int getWidth() {
		return width;
	}
	
	public void setWidth(int width) {
		this.width = width;
	}
	
	public int getHeight() {
		return height;
	}
	
	public void setHeight(int height) {
		this.height = height;
	}
	
	// accept func for visiter pattern
	public void accept(ItemVisitor vis) {
		vis.visit(this);
	}
}
