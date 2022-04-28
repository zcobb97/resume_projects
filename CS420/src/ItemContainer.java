import java.util.ArrayList;

public class ItemContainer implements ItemComponent {
	private ItemContainer parent;
	private ArrayList<ItemComponent> items = new ArrayList<ItemComponent>();
	private String name;
	private double price;
	private int x;
	private int y;
	private int length;
	private int width;
	private int height;
	
	// consructors
	public ItemContainer(String name, double price, int x, int y, int length,
			int width, int height) {
		super();
		this.name = name;
		this.price = price;
		this.x = x;
		this.y = y;
		this.length = length;
		this.width = width;
		this.height = height;
	}
	
	public ItemContainer(String name) {
		this.parent = null;
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
	
	public ArrayList<ItemComponent> getItems() {
		return items;
	}
	
	// getters and setters
	public void addItem(ItemComponent item) {
		item.setParent(this);
		this.items.add(item);
	}
	
	public void removeItem(ItemComponent item) {
		this.items.remove(item);
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
	
	public void setY(int y) {
		this.y = y;
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
	
	// accept func for visitor pattern
	public void accept(ItemVisitor vis) {
		vis.visit(this);
	}
	
	// static helper funcs
	// convert item container to list of all children, children's children, etc.
	public static ArrayList<ItemComponent> toArrayList(ItemComponent item) {
		ArrayList<ItemComponent> items = new ArrayList<ItemComponent>();
		if (item instanceof ItemContainer) {
			items.add(item);
			
			((ItemContainer) item).getItems().forEach(i -> {
				items.addAll(ItemContainer.toArrayList(i));
			});
		} else {
			items.add(item);
		}
		return items;
	}
}
