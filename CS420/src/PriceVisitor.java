

public class PriceVisitor implements ItemVisitor {
	private double price;
	
	public void visit(Item item) {
		price += item.getPrice();
	}
	
	public void visit(ItemContainer itemContainer) {
		price += itemContainer.getPrice();
		for (int i = 0; i < itemContainer.getItems().size(); i++) {
			ItemComponent item = itemContainer.getItems().get(i);
			if (item instanceof Item) visit((Item) item);
			if (item instanceof ItemContainer) visit((ItemContainer) item);
		}
	}

	public double getPrice() {
		return price;
	}
}
