import {Component} from "@angular/core";
import {OrderbookService} from "./orderbook.service";
import {OidcSecurityService} from "angular-auth-oidc-client";
import {UserDetails} from "./user.details";

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

  username = "";
  userDetails : UserDetails;

  constructor(private orderbookService: OrderbookService,
              private oidcSecurityService: OidcSecurityService){

    this.refreshData();
    this.refreshUser();
  }

  refreshUser() {
    this.orderbookService.getUserDetails().subscribe(
      (userDetails) => this.userDetails = userDetails,
      (error) => console.log(error)
    );

    this.oidcSecurityService.getUserData().subscribe(
      (user) => this.username = user.preferred_username,
      (error) => console.error(error)
    );
  }

  createOrder() {
    this.orderbookService.placeOrder(this.user, this.amount, this.price, this.operation).subscribe(
      (id) => {
        this.refreshData();
        this.refreshUser();
        console.log(id)
      },
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
