package com.ecommify.product.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

/**
 * Controlador de health check para Kubernetes.
 * <p>
 * Expone el endpoint /actuator/health usado por liveness y readiness
 * probes en el Deployment de Kubernetes.
 * </p>
 */
@RestController
public class HealthController {

    /**
     * Responde con el estado actual del servicio.
     *
     * @return mapa con status "UP" (200 OK)
     */
    @GetMapping("/actuator/health")
    public ResponseEntity<Map<String, String>> health() {
        return ResponseEntity.ok(Map.of("status", "UP"));
    }
}
