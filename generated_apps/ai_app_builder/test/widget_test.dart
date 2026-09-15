import 'package:flutter_test/flutter_test.dart';
import 'package:ai_app_builder/main.dart';

void main() {
  testWidgets('generated app opens', (tester) async {
    await tester.pumpWidget(const NovaixGeneratedApp());
    expect(find.text('AI App Builder'), findsOneWidget);
    expect(find.text('Get Started'), findsOneWidget);
  });
}
