package com.ecommify.product.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Map;

/**
 * Controlador REST para el catalogo de productos.
 * Expone operaciones CRUD sobre productos via API REST.
 */
@RestController
@RequestMapping("/api/v1/products")
public class ProductController {

    /**
     * Lista todos los productos disponibles.
     * <p>
     * Retorna un array JSON con productos de ejemplo
     * (id, nombre, precio).
     * </p>
     *
     * @return lista de productos con status 200 OK
     */
    @GetMapping
    public ResponseEntity<List<Map<String, Object>>> listProducts() {
        var products = List.of(
                Map.<String, Object>of("id", 1, "name", "Laptop", "price", 999.99),
                Map.<String, Object>of("id", 2, "name", "Mouse", "price", 29.99),
                Map.<String, Object>of("id", 3, "name", "Keyboard", "price", 79.99)
        );
        return ResponseEntity.ok(products);
    }
}
