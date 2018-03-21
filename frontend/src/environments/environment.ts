// The file contents for the current environment will overwrite these during build.
// The build system defaults to the dev environment which uses `environment.ts`, but if you do
// `ng build --env=prod` then `environment.prod.ts` will be used instead.
// The list of which env maps to which file can be found in `.angular-cli.json`.

export const environment = {
  production: false,

  pyramidUrl: "http://localhost:6543",
  angularUrl: "http://localhost:4200",
  authUrl: "http://10.52.52.103:8080/auth/realms/master"
};
