import { BrowserModule } from '@angular/platform-browser';
import { FormsModule } from '@angular/forms';
import {HTTP_INTERCEPTORS, HttpClientModule} from '@angular/common/http';


import {
  AuthModule,
  OidcSecurityService,
  OpenIDImplicitFlowConfiguration,
  OidcConfigService,
  AuthWellKnownEndpoints
} from 'angular-auth-oidc-client';

import { AppComponent } from './app.component';
import {OrderbookComponent} from "./orderbook/orderbook.component";
import {OrderbookService} from "./orderbook/orderbook.service";
import {OrderComponent} from "./orderbook/order/order.component";
import {UnauthorizedComponent} from "./unauthorized/unauthorized.component";
import {AppRoutingModule} from "./app.router.module";
import {AuthorizationGuard} from "./guard";
import {AuthInterceptor} from "./interceptor";
import {environment} from '../environments/environment';
import {NgModule} from '@angular/core';

@NgModule({
  declarations: [
    AppComponent,
    OrderbookComponent,
    OrderComponent,
    UnauthorizedComponent
  ],
  imports: [
    BrowserModule,
    FormsModule,
    HttpClientModule,
    AuthModule.forRoot(),
    AppRoutingModule
  ],
  providers: [
    OrderbookService,
    OidcConfigService,
    AuthorizationGuard,
    {
      provide: HTTP_INTERCEPTORS, useClass: AuthInterceptor, multi: true
    }
  ],
  bootstrap: [AppComponent]
})
export class AppModule {

  constructor(
    private oidcSecurityService: OidcSecurityService,
  ) {

      const openIDImplicitFlowConfiguration = new OpenIDImplicitFlowConfiguration();
      openIDImplicitFlowConfiguration.stsServer = ''; // damn
      openIDImplicitFlowConfiguration.redirect_url = environment.angularUrl;
      openIDImplicitFlowConfiguration.client_id = 'resefex';
      openIDImplicitFlowConfiguration.response_type = 'id_token token';
      openIDImplicitFlowConfiguration.scope = 'openid';
      openIDImplicitFlowConfiguration.post_logout_redirect_uri = environment.angularUrl + '/unauthorized';
      openIDImplicitFlowConfiguration.start_checksession = false;
      openIDImplicitFlowConfiguration.silent_renew = true;
      openIDImplicitFlowConfiguration.silent_renew_url = environment.angularUrl;
      openIDImplicitFlowConfiguration.post_login_route = environment.angularUrl;
      // HTTP 403
      openIDImplicitFlowConfiguration.forbidden_route = '/forbidden';
      // HTTP 401
      openIDImplicitFlowConfiguration.unauthorized_route = '/unauthorized';
      openIDImplicitFlowConfiguration.log_console_warning_active = true;
      openIDImplicitFlowConfiguration.log_console_debug_active = true;
      openIDImplicitFlowConfiguration.max_id_token_iat_offset_allowed_in_seconds = 10;

      const authWellKnownEndpoints = new AuthWellKnownEndpoints();
      authWellKnownEndpoints.issuer = environment.authUrl;

      authWellKnownEndpoints.jwks_uri = environment.authUrl+'/protocol/openid-connect/certs';
      authWellKnownEndpoints.authorization_endpoint = environment.authUrl+'/protocol/openid-connect/auth';
      authWellKnownEndpoints.token_endpoint = environment.authUrl+'/protocol/openid-connect/token';
      authWellKnownEndpoints.userinfo_endpoint = environment.authUrl+'/protocol/openid-connect/userinfo';
      authWellKnownEndpoints.end_session_endpoint = environment.authUrl+'/protocol/openid-connect/logout';
      authWellKnownEndpoints.check_session_iframe = environment.authUrl+'/protocol/openid-connect/login-status-iframe.html';
      authWellKnownEndpoints.introspection_endpoint = environment.authUrl+'/protocol/openid-connect/token/introspect';

      this.oidcSecurityService.setupModule(openIDImplicitFlowConfiguration, authWellKnownEndpoints);

  }
}
