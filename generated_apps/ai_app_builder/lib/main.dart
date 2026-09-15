import 'package:flutter/material.dart';

void main() => runApp(const NovaixGeneratedApp());

class NovaixGeneratedApp extends StatelessWidget {
  const NovaixGeneratedApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'AI App Builder',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF5546E8)),
        useMaterial3: true,
      ),
      home: const HomeScreen(),
    );
  }
}

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});
  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final screens = <String>['Splash', 'Onboarding', 'Home', 'Primary Workflow', 'History', 'Settings'];
  int selected = 0;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('AI App Builder')),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
            Text(screens[selected], style: Theme.of(context).textTheme.headlineMedium),
            const SizedBox(height: 16),
            const Card(child: Padding(
              padding: EdgeInsets.all(18),
              child: Text('Create a professional offline-first Flutter app builder with secure generation, verification and downloadable source projects'),
            )),
            const Spacer(),
            FilledButton(
              onPressed: () => ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('NOVAIX generated workflow is ready')),
              ),
              child: const Text('Get Started'),
            ),
          ]),
        ),
      ),
      bottomNavigationBar: NavigationBar(
        selectedIndex: selected,
        onDestinationSelected: (value) => setState(() => selected = value),
        destinations: screens.take(5).map((name) => NavigationDestination(
          icon: const Icon(Icons.apps_rounded), label: name,
        )).toList(),
      ),
    );
  }
}
