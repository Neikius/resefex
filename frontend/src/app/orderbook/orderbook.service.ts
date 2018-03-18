import {Injectable} from "@angular/core";
import {Http, Response, RequestOptions, Headers} from "@angular/http";
import "rxjs/Rx";

@Injectable()
export class OrderbookService {
  constructor(private http: Http) {}
  getOrderbookBids() {
    return this.http.get('http://localhost:6543/api/v1/orderbook/bids')
      .map(
        (response: Response) => {
          return response.json();
        }
      );
  }
  getOrderbookAsks() {
    return this.http.get('http://localhost:6543/api/v1/orderbook/asks')
      .map(
        (response: Response) => {
          return response.json();
        }
      );
  }
  placeOrder(user: number, amount: number, price: number, type: string) {
    let url = 'http://localhost:6543/api/v1/order/limit/'+type+'/'+amount+'/'+price;
    let myHeaders = new Headers();
    myHeaders.append('Authorization', 'Bearer ' + user);
    let options = new RequestOptions({headers: myHeaders});
    return this.http.put( url, null, options)
      .map(
        (response: Response) => {
          return response.json();
        }
      );
  }
}
