import { NgModule } from '@angular/core';
import { Routes, RouterModule, PreloadAllModules } from '@angular/router';

import { OrderbookComponent } from "./orderbook/orderbook.component";
import { UnauthorizedComponent } from './unauthorized/unauthorized.component';
import {AuthorizationGuard} from "./guard";

const routes: Routes = [
  { path: '', redirectTo: 'orderbook', pathMatch: 'full', canActivate: [AuthorizationGuard] },
  { path: 'orderbook', component: OrderbookComponent, canActivate: [AuthorizationGuard] },
  { path: 'forbidden', component: UnauthorizedComponent },
  { path: 'unauthorized', component: UnauthorizedComponent },
  { path: '**', redirectTo: 'orderbook', canActivate: [AuthorizationGuard] }
];

@NgModule({
  imports: [
    RouterModule.forRoot(routes, {
      preloadingStrategy: PreloadAllModules
    })
  ],
  exports: [RouterModule]
})
export class AppRoutingModule { }
