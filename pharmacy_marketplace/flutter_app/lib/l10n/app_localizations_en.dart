// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for English (`en`).
class AppLocalizationsEn extends AppLocalizations {
  AppLocalizationsEn([String locale = 'en']) : super(locale);

  @override
  String get appTitle => 'Pharmacy Marketplace';

  @override
  String get homeTitle => 'Find Medicines Near You';

  @override
  String get searchHint => 'Search medicines...';

  @override
  String get login => 'Login';

  @override
  String get register => 'Register';

  @override
  String get logout => 'Logout';

  @override
  String get phoneNumber => 'Phone Number';

  @override
  String get password => 'Password';

  @override
  String get submit => 'Submit';

  @override
  String get cancel => 'Cancel';

  @override
  String get loading => 'Loading...';

  @override
  String get error => 'An error occurred';

  @override
  String get noResults => 'No results found';

  @override
  String get sortByPrice => 'Sort by Price';

  @override
  String get filterByAvailability => 'Filter by Availability';

  @override
  String get price => 'Price';

  @override
  String get distance => 'Distance';

  @override
  String get available => 'Available';

  @override
  String get notAvailable => 'Not Available';
}
