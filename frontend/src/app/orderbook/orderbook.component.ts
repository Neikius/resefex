import {Component} from "@angular/core";
import {OrderbookService} from "./orderbook.service";

@Component({
  selector: 'app-orderbook',
  templateUrl: './orderbook.component.html',

})
export class OrderbookComponent {
  bids = [];
  asks = [];

  user: number = 1;
  amount: number = 1;
  price: number = 1;
  operation: string = "ASK";

  constructor(private orderbookService: OrderbookService){}

  createOrder() {
    this.orderbookService.placeOrder(this.user, this.amount, this.price, this.operation).subscribe(
      (id) => console.log(id),
      (error) => console.error(error)
    );
  }

  refreshData() {
    this.orderbookService.getOrderbookBids().subscribe(
      (bids) => {
        this.bids = bids
      },
      (error) => console.error(error)
    );
    this.orderbookService.getOrderbookAsks().subscribe(
      (asks) => {
        this.asks = asks
      },
      (error) => console.error(error)
    );
  }
}
