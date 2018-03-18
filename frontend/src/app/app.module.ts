import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { HttpModule } from '@angular/http';

import { AppComponent } from './app.component';
import {OrderbookComponent} from "./orderbook/orderbook.component";
import {OrderbookService} from "./orderbook/orderbook.service";
import {OrderComponent} from "./orderbook/order/order.component";


@NgModule({
  declarations: [
    AppComponent,
    OrderbookComponent,
    OrderComponent
  ],
  imports: [
    BrowserModule,
    FormsModule,
    HttpModule
  ],
  providers: [OrderbookService],
  bootstrap: [AppComponent]
})
export class AppModule { }
