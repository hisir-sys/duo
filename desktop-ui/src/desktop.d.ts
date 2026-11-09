export {};
declare global {
  interface Window {
    duoDesktop: {
      platform: string;
      shell: string;
      backend: {
        invoke: (method: string, args?: Record<string, unknown>) => Promise<any>;
      };
    };
  }
}
