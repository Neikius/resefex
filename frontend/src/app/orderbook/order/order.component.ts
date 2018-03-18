import {Component, Input} from "@angular/core";

class OrderBookEntry {
  id: string;
  price: number;
  amount: number;
  type: string;
  owner_id: number;
}

@Component({
  selector: "app-order",
  templateUrl: "./order.component.html"
})
export class OrderComponent {
  @Input() entry: OrderBookEntry
}
