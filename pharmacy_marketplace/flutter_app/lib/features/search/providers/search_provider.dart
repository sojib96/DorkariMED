import 'package:flutter_riverpod/flutter_riverpod.dart';

/// Search state and methods — Phase 3 implementation.
class SearchState {
  final String query;
  final List<dynamic> results;
  final bool isLoading;

  const SearchState({
    this.query = '',
    this.results = const [],
    this.isLoading = false,
  });
}

class SearchNotifier extends StateNotifier<SearchState> {
  SearchNotifier() : super(const SearchState());

  // Phase 3: implement search, filter, sort
}

final searchProvider = StateNotifierProvider<SearchNotifier, SearchState>((ref) {
  return SearchNotifier();
});
