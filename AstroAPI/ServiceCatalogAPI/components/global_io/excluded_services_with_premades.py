def excluded_services_with_premades(premades: list[object], excluded_services: list[str]):
    ignore_in_excluded_services = []
    for premade in premades:
        if premade.service not in excluded_services:
            excluded_services.append(premade.service)
        ignore_in_excluded_services.append(premade.service)
    return ignore_in_excluded_services