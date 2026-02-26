import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AppLayout } from '@/components/layout/app-layout';
import { Dashboard } from '@/pages/dashboard';
import { Status } from '@/pages/status';
import { Sessions } from '@/pages/sessions';
import { IoPage } from '@/pages/io';
import { AvatarPage } from '@/pages/avatar';
import { ScriptingPage } from '@/pages/scripting';
import { MarketplacePage } from '@/pages/marketplace';
import { OSCPage } from '@/pages/osc';
import { RestApiPage } from '@/pages/rest_api';
import { Integrations } from '@/pages/integrations';
import { Contacts } from '@/pages/contacts';
import { Chat } from '@/pages/chat';
import { Tools } from '@/pages/tools';
import { Help } from '@/pages/help';
import { Settings } from '@/pages/settings';
import { Inventory } from '@/pages/inventory';
import { ProtoFluxPage } from '@/pages/protoflux';
import { ResoniteLinkPage } from '@/pages/resonite_link';
import { World } from '@/pages/world';
import { Control } from '@/pages/control';
import { Map } from '@/pages/map';
import { Apps } from '@/pages/apps';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: 1, staleTime: 15_000 },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <AppLayout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/status" element={<Status />} />
            <Route path="/sessions" element={<Sessions />} />
            <Route path="/io" element={<IoPage />} />
            <Route path="/avatar" element={<AvatarPage />} />
            <Route path="/scripting" element={<ScriptingPage />} />
            <Route path="/marketplace" element={<MarketplacePage />} />
            <Route path="/osc" element={<OSCPage />} />
            <Route path="/rest-api" element={<RestApiPage />} />
            <Route path="/integrations" element={<Integrations />} />
            <Route path="/contacts" element={<Contacts />} />
            <Route path="/chat" element={<Chat />} />
            <Route path="/tools" element={<Tools />} />
            <Route path="/help" element={<Help />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="/inventory" element={<Inventory />} />
            <Route path="/protoflux" element={<ProtoFluxPage />} />
            <Route path="/resonite-link" element={<ResoniteLinkPage />} />
            <Route path="/world" element={<World />} />
            <Route path="/control" element={<Control />} />
            <Route path="/map" element={<Map />} />
            <Route path="/apps" element={<Apps />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </AppLayout>
      </Router>
    </QueryClientProvider>
  );
}

export default App;
