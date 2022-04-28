

public class MarketValueVisitor implements ItemVisitor {
	private double marketValue;
	
	public void visit(Item item) {
		marketValue += item.getMarketValue();
	}
	
	public void visit(ItemContainer itemContainer) {
		for (int i = 0; i < itemContainer.getItems().size(); i++) {
			ItemComponent item = itemContainer.getItems().get(i);
			if (item instanceof Item) visit((Item) item);
			if (item instanceof ItemContainer) visit((ItemContainer) item);
		}
	}

	public double getMarketValue() {
		return marketValue;
	}
}
