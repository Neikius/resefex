import {Injectable} from "@angular/core";
import {HttpClient, HttpResponse } from '@angular/common/http';
import "rxjs/Rx";
import {OrderBookEntry} from "./order/orderbookentry";
import {UserDetails} from "./user.details";
import { environment } from '../../environments/environment';

@Injectable()
export class OrderbookService {

  constructor(private http: HttpClient) {}
  getOrderbookBids() {
    return this.http.get<OrderBookEntry[]>(environment.pyramidUrl + '/api/v1/orderbook/bids')
      .map(
        (bids) => {
          return bids;
        }
      );
  }
  getOrderbookAsks() {
    return this.http.get<OrderBookEntry[]>(environment.pyramidUrl + '/api/v1/orderbook/asks')
      .map(
        (asks) => {
          return asks;
        }
      );
  }
  placeOrder(user: number, amount: number, price: number, type: string) {
    let url = environment.pyramidUrl + '/api/v1/order/limit/'+type+'/'+amount+'/'+price;
    return this.http.put( url, null, {headers: {'User': user + ''}} )
      .map(
        (response: HttpResponse<String>) => {
          return response;
        }
      );
  }
  getUserDetails() {
    let url = environment.pyramidUrl + '/api/v1/user/details';
    return this.http.get<UserDetails>(url);
  }
}
