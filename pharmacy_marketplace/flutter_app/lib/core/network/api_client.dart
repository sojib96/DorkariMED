import 'package:dio/dio.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

/// Singleton HTTP client configured for the marketplace API.
///
/// In Phase 1 this will get JWT token injection via interceptor.
class ApiClient {
  late final Dio _dio;
  final _storage = const FlutterSecureStorage();

  ApiClient({String? baseUrl}) {
    _dio = Dio(
      BaseOptions(
        baseUrl: baseUrl ?? 'http://10.0.2.2:8000/api/v1/',
        connectTimeout: const Duration(seconds: 10),
        receiveTimeout: const Duration(seconds: 15),
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
      ),
    );

    _dio.interceptors.add(AuthInterceptor(_storage, _dio));
  }

  Dio get client => _dio;
}

/// Interceptor that attaches JWT token to requests and handles 401 refresh.
class AuthInterceptor extends Interceptor {
  final FlutterSecureStorage _storage;
  final Dio _dio;

  AuthInterceptor(this._storage, this._dio);

  @override
  void onRequest(
    RequestOptions options,
    RequestInterceptorHandler handler,
  ) async {
    // Phase 1: load access token from secure storage and attach
    final token = await _storage.read(key: 'access_token');
    if (token != null) {
      options.headers['Authorization'] = 'Bearer $token';
    }
    handler.next(options);
  }

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) {
    // Phase 1: handle 401, attempt token refresh, retry
    handler.next(err);
  }
}
