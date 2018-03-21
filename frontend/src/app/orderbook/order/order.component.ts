import {Component, Input} from "@angular/core";
import {OrderBookEntry} from "./orderbookentry";

@Component({
  selector: "app-order",
  templateUrl: "./order.component.html"
})
export class OrderComponent {
  @Input() entry: OrderBookEntry
}
