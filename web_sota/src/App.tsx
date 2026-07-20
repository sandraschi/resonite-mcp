import { AppLayout } from "@/components/layout/app-layout";
import { PresenceGate } from "@/components/presence-gate";
import Logging from "@/pages/Logging";
import { AgentTools } from "@/pages/agent-tools";
import { Apps } from "@/pages/apps";
import { AvatarPage } from "@/pages/avatar";
import { Chat } from "@/pages/chat";
import { Contacts } from "@/pages/contacts";
import { Control } from "@/pages/control";
import { Dashboard } from "@/pages/dashboard";
import { Help } from "@/pages/help";
import { Integrations } from "@/pages/integrations";
import { Inventory } from "@/pages/inventory";
import { IoPage } from "@/pages/io";
import { Map } from "@/pages/map";
import { MarketplacePage } from "@/pages/marketplace";
import { OSCPage } from "@/pages/osc";
import { ProtoFluxPage } from "@/pages/protoflux";
import { ResoniteLinkPage } from "@/pages/resonite_link";
import { RestApiPage } from "@/pages/rest_api";
import { ScriptingPage } from "@/pages/scripting";
import { SearchPage } from "@/pages/search";
import { Sessions } from "@/pages/sessions";
import { Settings } from "@/pages/settings";
import { Status } from "@/pages/status";
import { Gallery } from "@/pages/gallery";
import { Tools } from "@/pages/tools";
import { World } from "@/pages/world";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import {
	Navigate,
	Route,
	BrowserRouter as Router,
	Routes,
} from "react-router-dom";

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
						<Route path="/agent-tools" element={<AgentTools />} />
						<Route path="/status" element={<Status />} />
						<Route path="/gallery" element={<Gallery />} />
						<Route
							path="*"
							element={
								<PresenceGate>
									<Routes>
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
										<Route
											path="/resonite-link"
											element={<ResoniteLinkPage />}
										/>
										<Route path="/world" element={<World />} />
										<Route path="/control" element={<Control />} />
										<Route path="/map" element={<Map />} />
										<Route path="/search" element={<SearchPage />} />
										<Route path="/apps" element={<Apps />} />
										<Route path="/logs" element={<Logging />} />
										<Route path="*" element={<Navigate to="/" replace />} />
									</Routes>
								</PresenceGate>
							}
						/>
					</Routes>
				</AppLayout>
			</Router>
		</QueryClientProvider>
	);
}

export default App;
